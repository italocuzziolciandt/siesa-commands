import logging
from typing import Optional
from feature_analyzer.codegenerator.code_generator_service_interface import (
    CodeGeneratorServiceInterface,
)
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from feature_analyzer.models.procedure_analysis_result_model import (
    ProcedureAnalysisResultModel,
)
from feature_analyzer.codegenerator.business.business_code_generator_from_procedure import (
    BusinessCodeGeneratorFromProcedure,
)
from feature_analyzer.feature_toggle import feature_toggle_instance

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
from generativeai.prompter_factory import PrompterFactory
from feature_analyzer.app_config import app_config_instance


class BusinessFullAICodeGeneratorFromProcedure(CodeGeneratorServiceInterface):
    """
    Service class responsible for orchestrating the code generation process from a given procedure.
    This class acts as a coordinator, utilizing CodeGenerator and DependencyProcessor to generate full code.
    """

    def __init__(self):
        """
        Initializes the GenerateCodeFromProcedureService with configurations and dependencies.

        Args:
            config_auth (ConfigAuthentication): The authentication configuration for the language model.
            model (str): The name of the language model to use.
            max_dependency_depth (int, optional): The maximum depth to process dependencies. Defaults to 1.
        """
        prompter = PrompterFactory.create_prompter(
            config_auth=app_config_instance.get_config_auth(),
            model=app_config_instance.backend_business_llm_model,
            use_agent=True,
        )

        self.code_generator_from_procedure = BusinessCodeGeneratorFromProcedure(
            prompter
        )
        self.logger = logging.getLogger(__name__)

    def generate(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        """
        Generates code for the entry point procedure and its dependencies.

        Args:
            data_wrapper (DataWrapperModel): The data wrapper containing the procedure analysis results.

        Returns:
            DataWrapperModel: The updated data wrapper with the generated code.
        """

        try:
            if (
                not feature_toggle_instance.is_backend_business_code_generation_enabled()
            ):
                self.logger.info(
                    "Business code generation is disabled. Skipping generation."
                )
                return data_wrapper

            self.logger.info("Starting code generation from procedures process...")

            entry_point_procedure: Optional[ProcedureAnalysisResultModel] = (
                self._get_entry_point_procedure(data_wrapper)
            )

            if not entry_point_procedure:
                error_message = "No entry point procedure found in the data wrapper."
                self.logger.error(error_message)
                raise ValueError(error_message)

            self.logger.info(
                f"Generating code for entry point procedure: {entry_point_procedure.procedure_name}"
            )

            ## GENERATE USING AGENT AND TEXT AS OUTPUT
            all_code = self.code_generator_from_procedure.generate_code_for_procedure_with_agent_as_str(
                entry_point_procedure,
                class_to_be_implemented="",
                parent_class_content="",
            )

            data_wrapper.output_code_full_content = all_code

            self.logger.info(f"Code generation from procedure completed.")
        except Exception as error:
            self.logger.error(
                f"Error on generating the backend business classes: {error}."
            )

        return data_wrapper

    def _get_entry_point_procedure(
        self, data_wrapper: DataWrapperModel
    ) -> Optional[ProcedureAnalysisResultModel]:
        """
        Helper method to retrieve the entry point procedure from the data wrapper.

        Args:
            data_wrapper (DataWrapperModel): The data wrapper containing the procedure analysis results.

        Returns:
            Optional[ProcedureAnalysisResultModel]: The entry point procedure, or None if not found.
        """
        return (
            data_wrapper.output_procedure_analysis_result[0]
            if data_wrapper.output_procedure_analysis_result
            else None
        )
