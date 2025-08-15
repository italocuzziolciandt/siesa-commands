import logging
from sql2doc.feature_analyzer.models.procedure_model import ProcedureModel
from sql2doc.feature_analyzer.models.data_wrapper_model import DataWrapperModel
from sql2doc.feature_analyzer.preparation.sql_script_sanitizer import SqlScriptSanitizer
from sql2doc.feature_analyzer.preparation.procedure_content_analyzer import (
    ProcedureContentAnalyzer,
)
from sql2doc.feature_analyzer.app_config import app_config_instance

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class PrepareProceduresContentService:
    """
    Prepares the content of stored procedures for analysis.
    """

    def __init__(self) -> None:
        """
        Initializes the PrepareProceduresContentService with the specified tiktoken model.

        Args:
            tiktoken_model (str): The name of the tiktoken model to use for tokenization.
        """
        self.sql_sanitizer = SqlScriptSanitizer()
        self.procedure_analyzer = ProcedureContentAnalyzer(
            app_config_instance.prepare_procedures_tiktoken_model
        )
        self.logger = logging.getLogger(__name__)

    def prepare_procedures_content(
        self, data_wrapper: DataWrapperModel
    ) -> DataWrapperModel:
        """
        Prepares the content of stored procedures by sanitizing and analyzing them.

        Args:
            data_wrapper (DataWrapperModel): The DataWrapperModel object containing the stored procedure files and content.

        Returns:
            DataWrapperModel: The DataWrapperModel object with the output_procedures_mapping field populated with the analyzed stored procedures.
        """
        try:
            result: list[ProcedureModel] = []

            for file_path, content in data_wrapper.procedure_files_mapping.items():
                if not content:
                    continue

                sanitized_content = self.sql_sanitizer.sanitize_sql_script(content)
                procedure_model = self.procedure_analyzer.analyze_content(
                    file_path, sanitized_content
                )
                result.append(procedure_model)

            data_wrapper.output_procedures_mapping = result
        except Exception as error:
            self.logger.error(f"Error on preparing the procedures content: {error}.")

        return data_wrapper
