import logging
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from feature_analyzer.documentation.use_cases.use_case_from_procedure_service import (
    UseCaseFromProcedureService,
)
from feature_analyzer.documentation.use_cases.use_case_from_app_file_service import (
    UseCaseFromAppFileService,
)
from feature_analyzer.documentation.use_cases.use_case_diagrams_service import (
    UseCaseDiagramsService,
)
from feature_analyzer.documentation.use_cases.use_case_consolidation_service import (
    UseCaseConsolidationService,
)
from feature_analyzer.common.step_execution_interface import StepExecutionInterface


class UseCaseExtractionStepService(StepExecutionInterface):
    use_case_from_procedure_service: UseCaseFromProcedureService
    use_case_from_app_file_service: UseCaseFromAppFileService
    use_case_diagrams_service: UseCaseDiagramsService
    use_case_consolidation_service: UseCaseConsolidationService

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.use_case_from_procedure_service = UseCaseFromProcedureService()
        self.use_case_from_app_file_service = UseCaseFromAppFileService()
        self.use_case_diagrams_service = UseCaseDiagramsService()
        self.use_case_consolidation_service = UseCaseConsolidationService()

    def execute(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        try:
            self.logger.info("Starting use cases analysis process...")

            self.use_case_from_procedure_service.analyze(data_wrapper)
            self.use_case_from_app_file_service.analyze(data_wrapper)
            self.use_case_consolidation_service.analyze(data_wrapper)
            self.use_case_diagrams_service.analyze(data_wrapper)

            self.logger.info("Use Cases analysis process completed.")

        except Exception as error:
            self.logger.error(f"Error on generating the use cases document: {error}.")

        return data_wrapper
