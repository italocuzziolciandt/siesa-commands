from feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


class AddDatabaseTableContentDelimitersPrompt(AnalyzerPrompt):
    def __init__(self, database_tables_content: str) -> None:
        self.database_tables_content = database_tables_content

    def get_system_message(self) -> str:
        return "You are a helpful Data assistant that prepares database table content for analysis."

    def get_user_message(self) -> str:
        return f"""
        Prepare the following database tables content for analysis. For each table, add delimiters to separated each table's content. The delimiters should be clear and specific to ensure that each table's content is easily identifiable.
        
        Use the delimiters:
        ###BeginTableContent
        <table definition>
        ###EndTableContent

        \n\n
        Here is the database tables content with all table definitions:
        {self.database_tables_content}
        """

    def get_messages(self) -> list[BaseMessage]:
        return [
            SystemMessage(content=self.get_system_message()),
            HumanMessage(content=self.get_user_message()),
        ]
