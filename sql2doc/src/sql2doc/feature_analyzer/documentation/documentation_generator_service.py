import logging
from sql2doc.feature_analyzer.models.data_wrapper_model import DataWrapperModel
from sql2doc.feature_analyzer.documentation.analyzer_service_interface import (
    AnalyzeServiceInterface,
)
from sql2doc.feature_analyzer.documentation.database_model.database_analyzer_indivually_service import (
    DatabaseAnalyzerIndivuallyService,
)
from sql2doc.feature_analyzer.documentation.use_cases.use_case_analyzer_service import (
    UseCaseAnalyzerService,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DocumentationGeneratorService(AnalyzeServiceInterface):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        self.logger.info("Starting documentation generation process...")
        doc_analyzers: list[AnalyzeServiceInterface] = [
            DatabaseAnalyzerIndivuallyService(),
            UseCaseAnalyzerService(),
        ]

        for analyzer in doc_analyzers:
            self.logger.info(
                f"Using doc analyzer generator: {analyzer.__class__.__name__}"
            )
            data_wrapper = analyzer.analyze(data_wrapper)

        self.logger.info("Documentation generation process completed.")

        return data_wrapper
