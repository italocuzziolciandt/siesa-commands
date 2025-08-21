import logging
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from feature_analyzer.common.step_execution_interface import (
    StepExecutionInterface,
)
from feature_analyzer.common.phase_execution_interface import PhaseExecutionInterface
from feature_analyzer.preparation.map_procedures_content_step_service import (
    MapProceduresContentStepService,
)
from feature_analyzer.preparation.map_tables_content_step_service import (
    MapTablesContentStepService,
)
from feature_analyzer.preparation.map_files_step_service import MapFilesStepService


class PreparationPhaseService(PhaseExecutionInterface):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def execute(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        self.logger.info("Starting preparation process...")
        preparation_steps: list[StepExecutionInterface] = [
            MapFilesStepService(),
            MapTablesContentStepService(),
            MapProceduresContentStepService(),
        ]

        for step in preparation_steps:
            self.logger.info(f"Using preparation step: {step.__class__.__name__}")
            data_wrapper = step.execute(data_wrapper)

        self.logger.info("Preparation process completed.")

        return data_wrapper

    def get_loading_log_message(self):
        return "[Preparation Phase] Executing..."

    def get_finished_log_message(self):
        return "[Preparation Phase] Finished executing."
