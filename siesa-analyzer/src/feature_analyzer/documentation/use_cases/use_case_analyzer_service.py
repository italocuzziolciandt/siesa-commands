from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from feature_analyzer.documentation.analyzer_service_interface import (
    AnalyzeServiceInterface,
)
from generativeai.prompter_interface import PrompterInterface
from feature_analyzer.feature_toggle import feature_toggle_instance
from feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from feature_analyzer.documentation.use_cases.prompts.use_case_from_procedure_prompt import (
    UseCasesFromProcedurePrompt,
)
from feature_analyzer.documentation.use_cases.prompts.use_case_from_app_file_prompt import (
    UseCasesFromApplicationFilePrompt,
)
from feature_analyzer.models.procedure_analysis_result_model import (
    ProcedureAnalysisResultModel,
)
from feature_analyzer.models.application_files_model import ApplicationFileModel
from feature_analyzer.documentation.use_cases.prompts.consolidates_use_cases_prompt import (
    ConsolidatesUseCasesPrompt,
)
from feature_analyzer.documentation.use_cases.prompts.sequence_diagram_prompt import (
    SequenceDiagramPrompt,
)
from feature_analyzer.documentation.use_cases.prompts.flow_diagram_prompt import (
    FlowDiagramPrompt,
)
from typing import Callable, TypeVar
from generativeai.prompter_factory import PrompterFactory
from feature_analyzer.app_config import app_config_instance

# Define a generic type for the items in the list
T = TypeVar("T")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class UseCaseAnalyzerService(AnalyzeServiceInterface):
    prompter: PrompterInterface

    def __init__(self):
        self.prompter = PrompterFactory.create_prompter(
            config_auth=app_config_instance.get_config_auth(),
            model=app_config_instance.use_case_analysis_llm_model,
            use_agent=True,
        )
        self.logger = logging.getLogger(__name__)
        self.max_workers = 20

    def analyze(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        try:

            if not feature_toggle_instance.is_use_case_doc_generation_enabled():
                self.logger.info("Use Case analysis is disabled. Skipping analysis.")
                return data_wrapper

            self.logger.info("Starting use case analysis process...")

            self.logger.info("Analyzing each procedure in parallel...")
            self.__process_in_parallel(
                data_wrapper.output_procedure_analysis_result,
                self.__generate_user_cases_from_procedure,
            )
            self.logger.info("The procedures were analyzed successfully.")

            self.logger.info("Analyzing each application file in parallel...")
            self.__process_in_parallel(
                data_wrapper.output_app_files_mapping,
                self.__generate_user_cases_from_application_files,
            )
            self.logger.info("The application files were analyzed successfully.")

            self.logger.info("Starting to consolidate use cases...")
            use_cases_result = self.__consolidate_use_cases(data_wrapper)
            self.logger.info("Consolidation of use cases completed.")

            self.logger.info("Starting to append diagrams...")
            self.__generate_diagrams(data_wrapper, use_cases_result)
            self.logger.info("Diagrams appended successfully.")

            data_wrapper.output_use_cases_doc_full_content = use_cases_result

            self.logger.info("Use Case analysis process completed.")

        except Exception as error:
            self.logger.error(f"Error on generating the use cases document: {error}.")

        return data_wrapper

    def __generate_diagrams(
        self, data_wrapper: DataWrapperModel, use_case_document: str
    ) -> str:
        prompt = SequenceDiagramPrompt(use_cases_content=use_case_document)
        sequence_diagram = self.prompter.get_content_from_invoke_llm_with_messages(
            prompt.get_messages()
        )

        prompt = FlowDiagramPrompt(use_cases_content=use_case_document)
        flow_diagram = self.prompter.get_content_from_invoke_llm_with_messages(
            prompt.get_messages()
        )

        data_wrapper.output_sequence_diagram_full_content = sequence_diagram
        data_wrapper.output_flow_diagram_full_content = flow_diagram

    def __consolidate_use_cases(self, data_wrapper: DataWrapperModel) -> str:
        procedures_result = "\n\n".join(
            [
                procedure.llm_use_cases_documentation
                for procedure in data_wrapper.output_procedure_analysis_result
                if procedure.llm_use_cases_documentation
            ]
        )

        app_files_result = "\n\n".join(
            [
                app_file.llm_use_cases_documentation
                for app_file in data_wrapper.output_app_files_mapping
                if app_file.llm_use_cases_documentation
            ]
        )

        result = f"{procedures_result}\n\n{app_files_result}"

        prompt = ConsolidatesUseCasesPrompt(use_cases_content=result)
        return self.prompter.get_content_from_invoke_llm_with_messages(
            prompt.get_messages()
        )

    def __process_in_parallel(
        self, items: list[T], processing_function: Callable[[T], None]
    ) -> None:
        """
        Processes a list of items in parallel using a thread pool.

        Args:
            items (List[T]): The list of items to process.
            processing_function (Callable[[T], None]): The function to apply to each item.
                                                     This function should accept a single item as input
                                                     and return None.
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(processing_function, item): item for item in items
            }

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    item = futures[future]  # Recover item in case of error.
                    self.logger.error(f"Error processing item: {item}. Error: {e}")

    def __generate_user_cases_from_application_files(
        self, application_file: ApplicationFileModel
    ) -> None:
        prompt = UseCasesFromApplicationFilePrompt(
            file_name=application_file.file_name,
            file_content=application_file.file_content,
            method_names=application_file.method_names,
        )

        application_file.llm_use_cases_documentation = (
            self.prompter.get_content_from_invoke_llm_with_messages(
                prompt.get_messages()
            )
        )

    def __generate_user_cases_from_procedure(
        self, procedure: ProcedureAnalysisResultModel
    ) -> None:
        prompt = UseCasesFromProcedurePrompt(
            procedure_name=procedure.procedure_name,
            procedure_content=procedure.procedure_orignal_content,
        )

        procedure.llm_use_cases_documentation = (
            self.prompter.get_content_from_invoke_llm_with_messages(
                prompt.get_messages()
            )
        )
