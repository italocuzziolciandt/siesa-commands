import re


class SqlScriptSanitizer:
    """
    Sanitizes SQL scripts by removing comments and unnecessary blocks.
    """

    def sanitize_sql_script(self, sql_script: str) -> str:
        """
        Sanitizes the given SQL script.

        Args:
            sql_script (str): The SQL script to sanitize.

        Returns:
            str: The sanitized SQL script.
        """
        sql_script = self._remove_drop_if_exists_blocks(sql_script)
        sql_script = self._remove_comments(sql_script)
        sql_script = self._remove_empty_lines(sql_script)
        return sql_script

    def _remove_drop_if_exists_blocks(self, sql_script: str) -> str:
        """
        Removes drop-if-exists blocks from the SQL script.

        Args:
            sql_script (str): The SQL script to process.

        Returns:
            str: The SQL script with drop-if-exists blocks removed.
        """
        return re.sub(
            r"(IF\s+EXISTS\s*\(\s*SELECT\s*\*.*?OBJECT_ID\(N'.*?'\).*?\)\s*\n.*?DROP\s+PROCEDURE\s+.*?\nGO\n)",
            "",
            sql_script,
            flags=re.DOTALL,
        )

    def _remove_comments(self, sql_script: str) -> str:
        """
        Removes comments enclosed in /* */ or /** */ from the SQL script.

        Args:
            sql_script (str): The SQL script to process.

        Returns:
            str: The SQL script with comments removed.
        """
        return re.sub(r"/\*[\s\S]*?\*/", "", sql_script)

    def _remove_empty_lines(self, sql_script: str) -> str:
        """
        Removes empty lines from the SQL script.

        Args:
            sql_script (str): The SQL script to process.

        Returns:
            str: The SQL script with empty lines removed.
        """
        lines = sql_script.splitlines()
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        return "\n".join(non_empty_lines)
