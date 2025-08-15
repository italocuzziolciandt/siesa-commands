import json


class TableReferenceModel:
    table_name: str
    type: str  # e.g., "SELECT", "INSERT", "UPDATE", "DELETE"

    def __init__(self, table_name: str, type: str) -> None:
        self.table_name = table_name
        self.type = type

    def to_dict(self):
        return self.__dict__


class ProcedureModel:
    procedure_name: str
    content: str
    parameters: list[str]
    calls: list[str]
    code_lines: int = 0
    tokens: int = 0
    tables: list[TableReferenceModel]
    table_names: list[str]

    def __init__(
        self,
        procedure_name: str,
        content: str,
        parameters: list[str] = None,
        calls: list[str] = None,
        code_lines: int = 0,
        tokens: int = 0,
        tables: list[TableReferenceModel] = None,
    ):
        self.procedure_name = procedure_name
        self.content = content
        self.parameters = parameters if parameters is not None else []
        self.calls = calls if calls is not None else []
        self.code_lines = code_lines
        self.tokens = tokens
        self.tables = tables if tables is not None else []
        self.table_names = self.__get_distinct_table_names()

    def to_dict(self):
        return {
            "procedure_name": self.procedure_name,
            "parameters": self.parameters,
            "calls": self.calls,
            "code_lines": self.code_lines,
            "tokens": self.tokens,
            "tables": (
                [table.to_dict() for table in self.tables] if self.tables else []
            ),  # Convert TableReference objects to dictionaries
            "table_names": self.table_names,
        }

    def __get_distinct_table_names(self) -> list[str]:
        table_names = [table.table_name for table in self.tables] if self.tables else []
        return list(set(table_names))

    def to_json(self) -> str:
        """
        Serialize the ProcedureModel instance to a JSON formatted string.

        :return: JSON string representation of the instance.
        """
        return json.dumps(self.__dict__, indent=4)
