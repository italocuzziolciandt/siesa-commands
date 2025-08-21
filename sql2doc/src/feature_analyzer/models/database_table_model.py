class DatabaseTableModel:
    name: str
    content: str
    code_lines: int = 0
    tokens: int = 0

    def __init__(self, name: str, content: str, tokens: int):
        self.name = name
        self.content = content
        self.code_lines = len(content.splitlines())
        self.tokens = tokens

    def get_content(self) -> str:
        return self.content
