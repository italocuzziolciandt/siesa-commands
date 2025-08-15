import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Set, Optional

from sql2doc.feature_analyzer.models.data_wrapper_model import DataWrapperModel
from sql2doc.feature_analyzer.models.procedure_model import ProcedureModel
from prompter.base import ConfigAuthentication
from sql2doc.generativeai.prompter_openai import PrompterOpenAI
from sql2doc.feature_analyzer.documentation.database_model.prompts.database_generate_mermaid_prompt import (
    DatabaseGenerateMermaidPrompt,
)
from sql2doc.feature_analyzer.documentation.analyzer_service_interface import (
    AnalyzeServiceInterface,
)
from sql2doc.feature_analyzer.models.procedure_analysis_result_model import (
    ProcedureAnalysisResultModel,
)
from sql2doc.feature_analyzer.models.database_table_model import DatabaseTableModel
from sql2doc.feature_analyzer.feature_toggle import feature_toggle_instance
from sql2doc.feature_analyzer.documentation.database_model.prompts.database_consolidate_diagrams_prompt import (
    DatabaseConsolidateDiagramsPrompt,
)
from sql2doc.generativeai.prompter_factory import PrompterFactory
from sql2doc.feature_analyzer.app_config import app_config_instance


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DatabaseAnalyzerIndivuallyService(AnalyzeServiceInterface):
    """
    Analyzes database procedures and generates Mermaid representations individually.

    This class orchestrates the analysis of database procedures, including fetching dependencies,
    generating Mermaid diagrams, and managing concurrent execution.
    """

    def __init__(self):
        """
        Initializes the DatabaseAnalyzerIndivuallyService.

        Args:
            config_auth (ConfigAuthentication): Authentication configuration for the Prompter.
            model (str): The name of the language model to use for generating Mermaid representations.
        """
        self.prompter = PrompterFactory.create_prompter(
            config_auth=app_config_instance.get_config_auth(),
            model=app_config_instance.database_diagrams_llm_model,
            use_agent=True,
        )
        self.max_workers = 20  # Number of threads for parallel processing
        self.logger = logging.getLogger(__name__)
        self.max_dependency_depth = (
            20  # Maximum recursion depth for procedure dependencies
        )

    def analyze(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        """
        Analyzes the database procedures starting from the entry point.

        This method retrieves procedure content, analyzes dependencies, and generates Mermaid diagrams
        if specified. It updates the DataWrapperModel with the analysis results.

        Args:
            procedure_entry_point (str): The name of the procedure to start the analysis from.
            data_wrapper (DataWrapperModel): The data wrapper containing database information.
            use_tables (bool, optional): Whether to include table content in the analysis. Defaults to False.
            should_generate_mermaid (bool, optional): Whether to generate Mermaid diagrams. Defaults to True.

        Returns:
            DataWrapperModel: The updated DataWrapperModel with the analysis results.
        """
        try:
            self.logger.info(
                f"Starting analysis for procedure entry point: {data_wrapper.procedure_entry_point_name}..."
            )

            procedure_content_mapping: list[ProcedureAnalysisResultModel] = (
                self._get_procedure_content_mapping(data_wrapper)
            )

            data_wrapper.output_procedure_analysis_result = procedure_content_mapping

            if feature_toggle_instance.is_database_model_generation_enabled():
                self.logger.info("Generating mermaid diagrams in parallel...")
                self._process_procedure_content_in_parallel(procedure_content_mapping)
                self.logger.info("Mermaid diagrams generated based on the procedures.")

                self.logger.info(
                    "Consolidating all diagrams as single representation..."
                )
                llm_result = self._consolidate_diagram_representations(
                    procedure_content_mapping
                )
                self.logger.info("Consolidation finished.")

                data_wrapper.output_database_model_full_content = llm_result
            else:
                self.logger.info(
                    "Skipping Mermaid generation as per configuration (it is disabled)."
                )
        except Exception as error:
            self.logger.error(f"Error on generating database model diagram: {error}.")

        return data_wrapper

    def _consolidate_diagram_representations(
        self, procedures_mapping: list[ProcedureAnalysisResultModel]
    ) -> str:
        """
        Concatenates the Mermaid representations from the analysis results.

        Args:
            procedures_mapping (List[ProcedureAnalysisResultModel]): A list of procedure analysis results.

        Returns:
            str: A string containing the concatenated Mermaid representations.
        """
        concatenated_diagrams = (
            "\n\n\n".join(
                [
                    f"{result.procedure_name}\n{result.llm_mermaid_representation}"
                    for result in procedures_mapping
                    if result.llm_mermaid_representation
                ]
            )
            if procedures_mapping
            else ""
        )

        prompt = DatabaseConsolidateDiagramsPrompt(concatenated_diagrams)
        return self.prompter.get_content_from_invoke_llm_with_messages(
            prompt.get_messages()
        )

    def _process_procedure_content_in_parallel(
        self, procedures_mapping: list[ProcedureAnalysisResultModel]
    ) -> None:
        """
        Processes procedure content in parallel to generate Mermaid representations.

        This method uses a ThreadPoolExecutor to process each procedure concurrently, improving performance
        when analyzing multiple procedures.

        Args:
            procedures_mapping (List[ProcedureAnalysisResultModel]): A list of procedure analysis results.
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._process_single_procedure, procedure): procedure
                for procedure in procedures_mapping
            }

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Error processing procedure: {e}")

    def _process_single_procedure(
        self, procedure_analysis_result: ProcedureAnalysisResultModel
    ) -> None:
        """
        Processes a single procedure to generate its Mermaid representation.

        This method invokes the language model to generate a Mermaid diagram based on the procedure's content.

        Args:
            procedure_analysis_result (ProcedureAnalysisResultModel): The analysis result for a single procedure.
        """
        self.logger.info(
            f"Generating mermaid representation for procedure: {procedure_analysis_result.procedure_name}"
        )

        prompt = DatabaseGenerateMermaidPrompt(
            feature_database_full_content=procedure_analysis_result.procedure_orignal_content
        )

        mermaid_representation = (
            self.prompter.get_content_from_invoke_llm_with_messages(
                prompt.get_messages()
            )
        )

        procedure_analysis_result.llm_mermaid_representation = mermaid_representation
        self.logger.info(
            f"Mermaid representation generated for procedure: {procedure_analysis_result.procedure_name}"
        )

    def _get_procedure_content_mapping(
        self, data_wrapper: DataWrapperModel
    ) -> list[ProcedureAnalysisResultModel]:
        """
        Retrieves content for the procedure and its dependencies.

        This method recursively fetches the content of the specified procedure and its dependencies,
        creating a mapping of procedure names to their content.

        Args:
            procedure_entry_point (str): The name of the procedure to start with.
            data_wrapper (DataWrapperModel): The data wrapper containing database information.
            use_tables (bool): Whether to include table content in the analysis.

        Returns:
            List[ProcedureAnalysisResultModel]: A list of ProcedureAnalysisResultModel objects.
        """
        processed_procedures: Set[str] = set()
        procedure_content_mapping: list[ProcedureAnalysisResultModel] = []

        self._get_procedure_and_dependency_content(
            data_wrapper.procedure_entry_point_name,
            data_wrapper,
            processed_procedures,
            procedure_content_mapping,
            data_wrapper.use_tables_in_procedure_analysis,
            current_depth=1,
        )

        return procedure_content_mapping

    def _get_procedure_and_dependency_content(
        self,
        procedure_name: str,
        data_wrapper: DataWrapperModel,
        processed_procedures: Set[str],
        procedure_content_mapping: list[ProcedureAnalysisResultModel],
        use_tables: bool,
        current_depth: int,
    ) -> None:
        """
        Recursively retrieves procedure content and dependencies.

        This method fetches the content of the specified procedure and recursively calls itself to fetch
        the content of its dependencies, up to a maximum depth.

        Args:
            procedure_name (str): The name of the procedure to retrieve.
            data_wrapper (DataWrapperModel): The data wrapper containing database information.
            processed_procedures (Set[str]): A set of procedure names that have already been processed.
            procedure_content_mapping (List[ProcedureAnalysisResultModel]): The list to store procedure content.
            use_tables (bool): Whether to include table content in the analysis.
            current_depth (int): The current recursion depth.
        """
        if current_depth > self.max_dependency_depth:
            self.logger.debug(
                f"Maximum dependency depth reached for procedure: {procedure_name}"
            )
            return

        if procedure_name in processed_procedures:
            self.logger.debug(f"Procedure already processed: {procedure_name}")
            return

        procedure = self._find_procedure(
            procedure_name, data_wrapper.output_procedures_mapping
        )

        if not procedure:
            self.logger.warning(f"Procedure not found: {procedure_name}")
            return

        processed_procedures.add(procedure_name)
        procedure_full_content = self._get_procedure_content(
            procedure_name, procedure, data_wrapper, use_tables
        )

        procedure_analysis_result = ProcedureAnalysisResultModel(
            procedure_name=procedure_name,
            procedure_orignal_content=procedure_full_content,
        )

        procedure_content_mapping.append(procedure_analysis_result)

        # Recursively process called procedures
        for called_procedure in procedure.calls:
            self._get_procedure_and_dependency_content(
                called_procedure,
                data_wrapper,
                processed_procedures,
                procedure_content_mapping,
                use_tables,
                current_depth=current_depth + 1,
            )

    def _find_procedure(
        self, procedure_name: str, procedures: list[ProcedureModel]
    ) -> Optional[ProcedureModel]:
        """
        Finds a procedure by name in a list of procedures.

        Args:
            procedure_name (str): The name of the procedure to find.
            procedures (List[ProcedureModel]): A list of ProcedureModel objects to search.

        Returns:
            Optional[ProcedureModel]: The found ProcedureModel, or None if not found.
        """
        return next((p for p in procedures if p.procedure_name == procedure_name), None)

    def _get_procedure_content(
        self,
        procedure_name: str,
        procedure: ProcedureModel,
        data_wrapper: DataWrapperModel,
        use_tables: bool,
    ) -> str:
        """
        Retrieves the content of a procedure, including table content if specified.

        Args:
            procedure_name (str): The name of the procedure.
            procedure (ProcedureModel): The ProcedureModel object.
            data_wrapper (DataWrapperModel): The data wrapper containing database information.
            use_tables (bool): Whether to include table content in the analysis.

        Returns:
            str: The content of the procedure, including table content if specified.
        """
        procedure_content = procedure.content
        content = f"\n-- Content of procedure {procedure_name} --\n" + procedure_content

        if use_tables:
            for table_name in procedure.table_names:
                content += self._get_table_content(
                    table_name, data_wrapper.output_tables_mapping
                )

        return content

    def _get_table_content(
        self, table_name: str, database_tables: list[DatabaseTableModel]
    ) -> str:
        """
        Retrieves the content of a table.

        Args:
            table_name (str): The name of the table.
            database_tables (List[DatabaseTableModel]): A list of DatabaseTableModel objects to search.

        Returns:
            str: The content of the table, or an empty string if not found.
        """
        table = next((t for t in database_tables if t.name == table_name), None)
        if table:
            content = f"\n-- Content of table {table_name} --\n" + table.content + "\n"
            return content
        else:
            self.logger.warning(f"Table not found: {table_name}")
            return ""
