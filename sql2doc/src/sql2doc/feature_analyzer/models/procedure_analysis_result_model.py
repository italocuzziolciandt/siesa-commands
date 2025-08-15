class ProcedureAnalysisResultModel:
    procedure_name: str
    procedure_orignal_content: str
    llm_mermaid_representation: str
    llm_use_cases_documentation: str = ""

    def __init__(
        self,
        procedure_name: str,
        procedure_orignal_content: str,
        llm_mermaid_representation: str = "",
    ) -> None:
        self.procedure_name = procedure_name
        self.procedure_orignal_content = procedure_orignal_content
        self.llm_mermaid_representation = llm_mermaid_representation
