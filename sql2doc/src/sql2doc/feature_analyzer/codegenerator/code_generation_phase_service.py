import logging
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from feature_analyzer.codegenerator.business.business_code_generation_step_service import (
    BusinessCodeGenerationStepService,
)
from feature_analyzer.codegenerator.entities.entities_code_generation_step_service import (
    EntitiesCodeGenerationStepService,
)
from feature_analyzer.common.phase_execution_interface import PhaseExecutionInterface
from feature_analyzer.common.step_execution_interface import StepExecutionInterface
from feature_analyzer.codegenerator.entities.db_context_code_generation_step_service import (
    DbContextCodeGenerationStepService,
)


class CodeGenerationPhaseService(PhaseExecutionInterface):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def execute(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        self.logger.info("Starting code generation process...")
        code_generators: list[StepExecutionInterface] = [
            EntitiesCodeGenerationStepService(),
            DbContextCodeGenerationStepService(),
            BusinessCodeGenerationStepService(max_dependency_depth=0),
        ]

        for code_generator in code_generators:
            self.logger.info(
                f"Using code generator step: {code_generator.__class__.__name__}"
            )
            data_wrapper = code_generator.execute(data_wrapper)

        self.logger.info("Code generation process completed.")

        return data_wrapper

    def get_loading_log_message(self):
        return "[Code Generation Phase] Executing..."

    def get_finished_log_message(self):
        return "[Code Generation Phase] Finished executing."
