class DatabaseTableModel:
    name: str
    content: str
    code_lines: int = 0
    tokens: int = 0
    new_name_convention: str = None

    def __init__(
        self, name: str, content: str, tokens: int, new_name_convention: str = None
    ):
        self.name = name
        self.content = content
        self.code_lines = len(content.splitlines())
        self.tokens = tokens
        self.new_name_convention = new_name_convention

    def get_content(self) -> str:
        return self.content
