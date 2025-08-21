import logging
from feature_analyzer.models.procedure_model import ProcedureModel
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from feature_analyzer.models.procedure_analysis_result_model import (
    ProcedureAnalysisResultModel,
)
from feature_analyzer.models.database_table_model import DatabaseTableModel
from typing import Set, Optional
from common.app_config import app_config_instance


class ProceduresExecutionGraphGenerator:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_dependency_depth = (
            app_config_instance.max_procedure_analysis_dependency_depth
        )

    def get_procedure_content_mapping(
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
        if (
            self.max_dependency_depth != -1
            and current_depth > self.max_dependency_depth
        ):
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
            self.logger.warning(f"⚠️ Procedure not found: {procedure_name}")
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
            self.logger.warning(f"⚠️ Table not found: {table_name}")
            return ""
