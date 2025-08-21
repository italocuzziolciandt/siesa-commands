import logging
from prompter.base import ConfigAuthentication
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from feature_analyzer.codegenerator.code_generation_phase_service import (
    CodeGenerationPhaseService,
)
from common.loading_animation import LoadingAnimation
from feature_analyzer.documentation.documentation_phase_service import (
    DocumentationPhaseService,
)
from common.app_config import app_config_instance
from generativeai.prompter_agent_tools import initialize_data_wrapper
from feature_analyzer.common.phase_execution_interface import PhaseExecutionInterface
from feature_analyzer.preparation.prepation_phase_service import PreparationPhaseService


class AnalyzerService:
    output_file_path: str

    def __init__(self, config_auth: ConfigAuthentication):
        """Initializes the AnalyzerService with the given configuration."""
        app_config_instance.set_config_auth(config_auth)
        self.logger = logging.getLogger(__name__)

    def analyze_feature(
        self,
        database_tables_file_path: str,
        procedure_entry_point_file_name: str,
        procedures_dir_path: str,
        application_files_dir_path: str,
        application_files_names_to_consider: list[str],
        output_file_path: str,
    ) -> None:
        """Analyzes a database feature given the specified file paths and generates code."""
        self.logger.info(f"Starting analysis for feature...")

        data_wrapper = DataWrapperModel(
            database_tables_file_path=database_tables_file_path,
            procedures_dir_path=procedures_dir_path,
            procedure_entry_point_file_name=procedure_entry_point_file_name,
            application_files_dir_path=application_files_dir_path,
            application_files_names_to_consider=application_files_names_to_consider,
            output_file_path=output_file_path,
        )

        self.logger.info(f"Initializing DataWrapperModel...")
        initialize_data_wrapper(data_wrapper)
        self.logger.info(f"DataWrapperModel initialized.")

        phases: list[PhaseExecutionInterface] = [
            PreparationPhaseService(),
            DocumentationPhaseService(),
            CodeGenerationPhaseService(),
        ]

        for phase in phases:
            with LoadingAnimation(message=phase.get_loading_log_message()):
                phase.execute(data_wrapper)

            self.logger.info(phase.get_finished_log_message())

        self.logger.info(
            f"Analysis and code generation completed successfully. Output written to {data_wrapper.output_timestamped_dir}."
        )
