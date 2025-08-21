from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from common.feature_toggle import feature_toggle_instance
from feature_analyzer.documentation.use_cases.base_use_case_generator_service import (
    BaseUseCaseGeneratorService,
)
from feature_analyzer.documentation.use_cases.prompts.consolidates_use_cases_prompt import (
    ConsolidatesUseCasesPrompt,
)


class UseCaseConsolidationService(BaseUseCaseGeneratorService):
    def analyze(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        try:
            if not feature_toggle_instance.is_use_case_flow_consolidation_enabled():
                self.logger.info("Use Case consolidation is disabled. Skipping.")
                return data_wrapper

            self.logger.info("Starting use case consolidation process...")

            consolidation_result = self.__consolidate_use_cases(data_wrapper)
            data_wrapper.output_use_cases_doc_full_content = consolidation_result

            self.logger.info("Use Case consolidation process completed.")

        except Exception as error:
            self.logger.error(
                f"Error on generating the consolidated use cases document: {error}."
            )

        return data_wrapper

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
