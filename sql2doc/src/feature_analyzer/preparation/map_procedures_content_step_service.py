import logging
from feature_analyzer.models.procedure_model import ProcedureModel
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from feature_analyzer.preparation.sql_script_sanitizer import SqlScriptSanitizer
from feature_analyzer.preparation.procedure_content_analyzer import (
    ProcedureContentAnalyzer,
)
from common.app_config import app_config_instance
from feature_analyzer.models.procedure_analysis_result_model import (
    ProcedureAnalysisResultModel,
)
from feature_analyzer.preparation.procedures_execution_graph_generator import (
    ProceduresExecutionGraphGenerator,
)
from feature_analyzer.common.step_execution_interface import StepExecutionInterface


class MapProceduresContentStepService(StepExecutionInterface):
    """
    Prepares the content of stored procedures for analysis.
    """

    def __init__(self) -> None:
        """
        Initializes the PrepareProceduresContentService with the specified tiktoken model.
        """
        self.sql_sanitizer = SqlScriptSanitizer()
        self.procedure_analyzer = ProcedureContentAnalyzer(
            app_config_instance.prepare_procedures_tiktoken_model
        )
        self.execution_graph_generator = ProceduresExecutionGraphGenerator()
        self.logger = logging.getLogger(__name__)

    def execute(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
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
                procedure_model: ProcedureModel = (
                    self.procedure_analyzer.analyze_content(
                        file_path, sanitized_content
                    )
                )
                result.append(procedure_model)

            data_wrapper.output_procedures_mapping = result

            procedure_content_mapping: list[ProcedureAnalysisResultModel] = (
                self.execution_graph_generator.get_procedure_content_mapping(
                    data_wrapper
                )
            )

            data_wrapper.output_procedure_analysis_result = procedure_content_mapping

        except Exception as error:
            self.logger.error(f"Error on preparing the procedures content: {error}.")

        return data_wrapper
