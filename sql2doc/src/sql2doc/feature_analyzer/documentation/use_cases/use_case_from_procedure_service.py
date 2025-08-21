from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from common.feature_toggle import feature_toggle_instance
from feature_analyzer.documentation.use_cases.prompts.use_case_from_procedure_prompt import (
    UseCasesFromProcedurePrompt,
)
from feature_analyzer.models.procedure_analysis_result_model import (
    ProcedureAnalysisResultModel,
)
from common.app_config import app_config_instance
from opentelemetry.trace import Status, StatusCode
from feature_analyzer.documentation.use_cases.base_use_case_generator_service import (
    BaseUseCaseGeneratorService,
)


class UseCaseFromProcedureService(BaseUseCaseGeneratorService):
    def analyze(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        try:

            if not feature_toggle_instance.is_use_case_from_procedure_enabled():
                self.logger.info(
                    "Use Case from procedure is disabled. Skipping analysis."
                )
                return data_wrapper

            self.logger.info("Starting use case from procedure analysis process...")

            self.logger.info("Analyzing each procedure in parallel...")
            self._process_in_parallel(
                data_wrapper.output_procedure_analysis_result,
                self.__generate_user_cases_from_procedure,
            )
            self.logger.info("The procedures were analyzed successfully.")

        except Exception as error:
            self.logger.error(
                f"Error on generating the use cases from procedure: {error}."
            )

        return data_wrapper

    def __generate_user_cases_from_procedure(
        self, procedure: ProcedureAnalysisResultModel
    ) -> None:
        with app_config_instance.tracer.start_as_current_span(
            "UseCasesFromProcedure",
            openinference_span_kind="chain",
        ) as span:
            try:
                span.set_input(
                    value={
                        "procedure_name": procedure.procedure_name,
                        "procedure_content": procedure.procedure_orignal_content,
                    }
                )

                prompt = UseCasesFromProcedurePrompt(
                    procedure_name=procedure.procedure_name,
                    procedure_content=procedure.procedure_orignal_content,
                )

                use_cases_content = (
                    self.prompter.get_content_from_invoke_llm_with_messages(
                        prompt.get_messages()
                    )
                )

                procedure.llm_use_cases_documentation = use_cases_content

                span.set_output(use_cases_content)
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
