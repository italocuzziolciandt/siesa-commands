class ApplicationFileModel:
    file_name: str
    file_content: str
    method_names: list[str]
    llm_use_cases_documentation: str

    def __init__(self, file_name: str, file_content: str, method_names: list[str]):
        self.file_name = file_name
        self.file_content = file_content
        self.method_names = method_names
