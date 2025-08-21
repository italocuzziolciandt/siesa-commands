import tiktoken
import logging
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from feature_analyzer.models.database_table_model import DatabaseTableModel
from feature_analyzer.preparation.table_content_parser import TableContentParser
from common.app_config import app_config_instance
from feature_analyzer.common.step_execution_interface import StepExecutionInterface


class MapTablesContentStepService(StepExecutionInterface):
    """
    Service responsible for preparing the content of database tables from a DataWrapperModel.
    It uses other classes to parse SQL, count tokens and create DatabaseTable objects.
    """

    def __init__(self):
        """
        Initializes the PrepareTablesContentService with a tokenizer model.

        Args:
            tiktoken_model (str): The name of the tiktoken model to use for tokenization.
        """
        self.tokenizer = tiktoken.encoding_for_model(
            app_config_instance.prepare_tables_tiktoken_model
        )
        self.table_content_parser = TableContentParser()
        self.logger = logging.getLogger(__name__)

    def execute(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        """
        Prepares the content of database tables by extracting individual tables
        from the SQL content, counting tokens, and creating DatabaseTable objects.

        Args:
            data_wrapper (DataWrapperModel): The DataWrapperModel containing the database tables content.

        Returns:
            DataWrapperModel: The updated DataWrapperModel with the extracted and prepared database tables.
        """
        try:
            tables = self._extract_tables(data_wrapper.database_tables_content)
            data_wrapper.output_tables_mapping = tables
        except Exception as error:
            self.logger.error(f"Error on preparing the tables content: {error}.")

        return data_wrapper

    def _extract_tables(self, database_tables_content: str) -> list[DatabaseTableModel]:
        """
        Extracts database tables from the given SQL content.

        Args:
            database_tables_content (str): The SQL content containing CREATE TABLE statements.

        Returns:
            List[DatabaseTable]: A list of DatabaseTable objects.
        """
        table_creation_statements = self.table_content_parser.split_into_statements(
            database_tables_content
        )
        tables: list[DatabaseTableModel] = []

        for statement in table_creation_statements:
            statement = statement.strip()
            if statement and statement.upper().startswith("CREATE TABLE"):
                table_name = self.table_content_parser.extract_table_name(statement)
                if table_name:
                    table_content = statement + ";"
                    tokens = self.__count_tokens(table_content)

                    table = DatabaseTableModel(
                        name=table_name,
                        content=table_content,
                        tokens=tokens,
                    )

                    tables.append(table)

        return tables

    def __count_tokens(self, text: str) -> int:
        tokens = self.tokenizer.encode(text)
        return len(tokens)
