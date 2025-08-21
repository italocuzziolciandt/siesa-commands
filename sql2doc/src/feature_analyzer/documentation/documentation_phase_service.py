import logging
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from feature_analyzer.common.step_execution_interface import (
    StepExecutionInterface,
)
from feature_analyzer.documentation.database_model.database_model_step_service import (
    DatabaseModelStepService,
)
from feature_analyzer.documentation.use_cases.use_case_extraction_step_service import (
    UseCaseExtractionStepService,
)
from feature_analyzer.common.phase_execution_interface import PhaseExecutionInterface


class DocumentationPhaseService(PhaseExecutionInterface):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def execute(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        self.logger.info("➡️ Starting documentation generation process...")
        doc_analyzers: list[StepExecutionInterface] = [
            DatabaseModelStepService(),
            UseCaseExtractionStepService(),
        ]

        for analyzer in doc_analyzers:
            self.logger.info(f"Using doc generator step: {analyzer.__class__.__name__}")
            data_wrapper = analyzer.execute(data_wrapper)

        self.logger.info("✅ Documentation generation process completed.")

        return data_wrapper

    def get_loading_log_message(self):
        return "⚙️ [Documentation Phase] Executing..."

    def get_finished_log_message(self):
        return "✅ [Documentation Phase] Finished executing."
