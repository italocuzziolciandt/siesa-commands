import re


class TableContentParser:
    """
    Responsible for parsing SQL content and extracting individual CREATE TABLE statements.
    """

    def __init__(self):
        self.table_creation_pattern = re.compile(
            r";\s*(?=(CREATE TABLE))", re.IGNORECASE | re.DOTALL
        )
        self.table_name_pattern = re.compile(r"CREATE TABLE\s+\[(.*?)\]", re.IGNORECASE)

    def split_into_statements(self, sql_content: str) -> list[str]:
        """
        Splits the SQL content into individual CREATE TABLE statements.

        Args:
            sql_content (str): The SQL content to split.

        Returns:
            List[str]: A list of CREATE TABLE statements.
        """
        return re.split(self.table_creation_pattern, sql_content)

    def extract_table_name(self, statement: str) -> str | None:
        """
        Extracts the table name from a CREATE TABLE statement.

        Args:
            statement (str): The CREATE TABLE statement.

        Returns:
            str | None: The table name, or None if no table name is found.
        """
        match = self.table_name_pattern.search(statement)
        return match.group(1) if match else None
