import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from feature_analyzer.documentation.database_model.prompts.database_generate_mermaid_prompt import (
    DatabaseGenerateMermaidPrompt,
)
from feature_analyzer.models.procedure_analysis_result_model import (
    ProcedureAnalysisResultModel,
)
from common.feature_toggle import feature_toggle_instance
from feature_analyzer.documentation.database_model.prompts.database_consolidate_diagrams_prompt import (
    DatabaseConsolidateDiagramsPrompt,
)
from generativeai.prompter_factory import PrompterFactory
from common.app_config import app_config_instance
from feature_analyzer.common.step_execution_interface import StepExecutionInterface
from opentelemetry.trace import Status, StatusCode


class DatabaseModelStepService(StepExecutionInterface):
    def __init__(self):
        """
        Initializes the DatabaseAnalyzerIndivuallyService.
        """
        self.prompter = PrompterFactory.create_prompter(
            config_auth=app_config_instance.get_config_auth(),
            model=app_config_instance.database_diagrams_llm_model,
            use_agent=True,
        )
        self.max_workers = 10  # Number of threads for parallel processing
        self.logger = logging.getLogger(__name__)

    def execute(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        try:
            self.logger.info(
                f"Starting analysis for procedure entry point: {data_wrapper.procedure_entry_point_name}..."
            )

            if feature_toggle_instance.is_database_model_generation_enabled():
                procedure_content_mapping = (
                    data_wrapper.output_procedure_analysis_result
                )

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
        with app_config_instance.tracer.start_as_current_span(
            "DatabaseModelFromProcedureGeneration",
            openinference_span_kind="chain",
        ) as span:
            try:
                span.set_input(
                    value={
                        "procedure_name": procedure_analysis_result.procedure_name,
                        "procedure_content": procedure_analysis_result.procedure_orignal_content,
                    }
                )

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

                procedure_analysis_result.llm_mermaid_representation = (
                    mermaid_representation
                )
                self.logger.info(
                    f"Mermaid representation generated for procedure: {procedure_analysis_result.procedure_name}"
                )

                span.set_output(mermaid_representation)
                span.set_status(Status(StatusCode.OK))

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return None
