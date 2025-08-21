import re
import os
import tiktoken
from feature_analyzer.models.procedure_model import ProcedureModel, TableReferenceModel


class ProcedureContentAnalyzer:
    """
    Analyzes the content of a stored procedure to extract relevant information.
    """

    def __init__(self, tiktoken_model: str) -> None:
        """
        Initializes the ProcedureContentAnalyzer with the specified tiktoken model.

        Args:
            tiktoken_model (str): The name of the tiktoken model to use for tokenization.
        """
        self.tokenizer = tiktoken.encoding_for_model(tiktoken_model)

    def analyze_content(self, file_path: str, content: str) -> ProcedureModel:
        """
        Analyzes the content of a stored procedure to extract its name, parameters, calls, tables, and other metadata.

        Args:
            file_path (str): The path to the file containing the stored procedure.
            content (str): The content of the stored procedure.

        Returns:
            ProcedureModel: A ProcedureModel object containing the extracted information.
        """
        procedure_name = self._extract_procedure_name(file_path)
        lines = content.splitlines()
        code_lines = len(lines)
        tokens = self._count_tokens(content)

        parameters = self._extract_parameters(content)
        calls = self._extract_procedure_calls(content)
        tables = self._extract_tables(content)

        return ProcedureModel(
            procedure_name=procedure_name,
            content=content,
            parameters=parameters,
            calls=calls,
            code_lines=code_lines,
            tokens=tokens,
            tables=tables,
        )

    def _extract_procedure_name(self, file_path: str) -> str:
        """
        Extracts the name of the stored procedure from the file path.

        Args:
            file_path (str): The path to the file containing the stored procedure.

        Returns:
            str: The name of the stored procedure.
        """
        return os.path.basename(file_path).split(".")[0]

    def _extract_parameters(self, content: str) -> list[str]:
        """
        Extracts the parameters of the stored procedure from its content.

        Args:
            content (str): The content of the stored procedure.

        Returns:
            List[str]: A list of the parameters of the stored procedure.
        """
        # Placeholder implementation. Needs to be implemented based on SQL dialect.
        return []

    def _extract_procedure_calls(self, content: str) -> list[str]:
        # The robust regex from before remains unchanged.
        exec_pattern = r"\b(EXEC|EXECUTE)\b\s+(?:@\w+\s*=\s*)?([\w\.]+)(?!\s*\()"

        matches = re.findall(exec_pattern, content, re.IGNORECASE)

        procedure_full_names = [match[1] for match in matches]

        seen_procedures = set()
        ordered_distinct_calls = []

        for name in procedure_full_names:
            # The schema is stripped just like before.
            procedure_name = name.split(".")[-1]

            # Only add the procedure to our list if it's the first time we've seen it.
            if procedure_name not in seen_procedures:
                seen_procedures.add(procedure_name)
                ordered_distinct_calls.append(procedure_name)

        return ordered_distinct_calls

    def _extract_tables(self, content: str) -> list[TableReferenceModel]:
        """
        Extracts the tables referenced in the content of the stored procedure.

        Args:
            content (str): The content of the stored procedure.

        Returns:
            List[TableReferenceModel]: A list of TableReferenceModel objects representing the tables referenced in the content.
        """
        select_pattern = r"SELECT\s+.+?\s+FROM\s+([\w\.]+)"
        insert_pattern = r"INSERT\s+INTO\s+([\w\.]+)"
        update_pattern = r"UPDATE\s+([\w\.]+)"
        delete_pattern = r"DELETE\s+FROM\s+([\w\.]+)"
        join_pattern = r"(?:INNER|LEFT|RIGHT)\s+JOIN\s+([\w\.]+)"

        select_tables = [
            (table, "SELECT")
            for table in re.findall(select_pattern, content, re.IGNORECASE)
        ]
        insert_tables = [
            (table, "INSERT")
            for table in re.findall(insert_pattern, content, re.IGNORECASE)
        ]
        update_tables = [
            (table, "UPDATE")
            for table in re.findall(update_pattern, content, re.IGNORECASE)
        ]
        delete_tables = [
            (table, "DELETE")
            for table in re.findall(delete_pattern, content, re.IGNORECASE)
        ]
        join_tables = [
            (table, "JOIN")
            for table in re.findall(join_pattern, content, re.IGNORECASE)
        ]

        tables: list[TableReferenceModel] = []

        for table_name, table_type in (
            select_tables + insert_tables + update_tables + delete_tables + join_tables
        ):
            tables.append(TableReferenceModel(table_name=table_name, type=table_type))

        # Remove duplicates based on table_name and type
        unique_tables = []
        seen = set()
        for table in tables:
            key = (table.table_name, table.type)
            if key not in seen:
                unique_tables.append(table)
                seen.add(key)

        # Sort the unique_tables list by table_name
        unique_tables.sort(key=lambda x: x.table_name)

        return unique_tables

    def _count_tokens(self, text: str) -> int:
        """
        Counts the number of tokens in the given text using the tokenizer.

        Args:
            text (str): The text to tokenize.

        Returns:
            int: The number of tokens in the text.
        """
        tokens = self.tokenizer.encode(text)
        return len(tokens)
