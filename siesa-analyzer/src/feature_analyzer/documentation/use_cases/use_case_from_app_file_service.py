from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from common.feature_toggle import feature_toggle_instance
from feature_analyzer.documentation.use_cases.prompts.use_case_from_app_file_prompt import (
    UseCasesFromApplicationFilePrompt,
)
from common.app_config import app_config_instance
from opentelemetry.trace import Status, StatusCode
from feature_analyzer.documentation.use_cases.base_use_case_generator_service import (
    BaseUseCaseGeneratorService,
)
from feature_analyzer.models.application_files_model import ApplicationFileModel


class UseCaseFromAppFileService(BaseUseCaseGeneratorService):
    def analyze(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        try:

            if not feature_toggle_instance.is_use_case_from_app_file_enabled():
                self.logger.info(
                    "Use Case from application file is disabled. Skipping analysis."
                )
                return data_wrapper

            self.logger.info(
                "Starting use case from application file analysis process..."
            )

            self.logger.info("Analyzing each application file in parallel...")
            self._process_in_parallel(
                data_wrapper.output_app_files_mapping,
                self.__generate_user_cases_from_application_files,
            )
            self.logger.info("The application files were analyzed successfully.")

        except Exception as error:
            self.logger.error(
                f"❌ Error on generating the use cases from application files: {error}."
            )

        return data_wrapper

    def __generate_user_cases_from_application_files(
        self, application_file: ApplicationFileModel
    ) -> None:

        with app_config_instance.tracer.start_as_current_span(
            "UseCasesFromAppFile",
            openinference_span_kind="chain",
        ) as span:
            try:
                span.set_input(
                    value={
                        "application_file": application_file.file_name,
                        "application_file_content": application_file.file_content,
                    }
                )

                prompt = UseCasesFromApplicationFilePrompt(
                    file_name=application_file.file_name,
                    file_content=application_file.file_content,
                    method_names=application_file.method_names,
                )

                use_cases_content = (
                    self.prompter.get_content_from_invoke_llm_with_messages(
                        prompt.get_messages()
                    )
                )

                application_file.llm_use_cases_documentation = use_cases_content

                span.set_output(use_cases_content)
                span.set_status(Status(StatusCode.OK))

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
