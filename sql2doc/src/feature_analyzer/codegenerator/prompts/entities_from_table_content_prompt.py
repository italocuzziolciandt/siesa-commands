from feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


class EntitiesFromTableContentPrompt(AnalyzerPrompt):
    def __init__(
        self,
        table_name: str,
        table_content: str,
    ) -> None:
        self.table_name = table_name
        self.table_content = table_content

    def get_system_message(self) -> str:
        return """
            You are a highly skilled C# developer with over many years of experience in software development. You are proficient in .NET framework, Brazor Applications, ASP.NET, and have a deep understanding of object-oriented programming, design patterns, and best coding practices. You are comfortable with both front-end and back-end development and have experience working in Agile environments. You are now tasked with providing insights, solutions, or code snippets related to C# development.

            Important:
            - Only answer if you have knowledge about the subject. If you don't have knowledge about it, ask for more information, provide some questions that the user can answer providing more context to you or as last resort, answer "Sorry, i don't have enough knowledge about the subject".
            - Clarify any assumptions made.
            - Include clear and concise explanations.
            """

    def get_user_message(self) -> str:
        return f"""
            We are modernizing an legacy application from Java to .NET C#. For the new application, we need to generate the Entities. The Entities are responsible for representing the database tables in the new application using Entity Framework Core.

            This is the database table that needs to map as an Entity:
            ```sql
            {self.table_content}
            ```

            Provide the Entity implementation, that represents and modernizes the tables.

            Strictly follow the example below:
            {self.__get_entity_example()}

            Coding Guidelines:
            - The entity should inherit from the BaseMaster base class.
            - The names of the entities are defined with an initial letter that describes their role and a 5-digit code where the first two define the service code and the remaining ones a unique code (example: E30010_Client).      
            - Use the annotations:
            -- SDKRequired: For database required fields.
            -- SDKStringLength: To defined the max length of varchar columns.

            Provide a **complete entity class implementation**, without summarizing or truncating the response. If the response exceeds the max output limit, continue generating until all services are fully covered.

            Important:
            - Ignore imports and namespaces, just provide the class implementation.
            - Don't make assumptions, provide the full entity implementation of the class.
            - Don't add any additional comments or explanations, just provide the code implementation.
        """

    def get_messages(self) -> list[BaseMessage]:
        return [
            SystemMessage(content=self.get_system_message()),
            HumanMessage(content=self.get_user_message()),
        ]

    def __get_entity_example(self) -> str:
        return """
        ```csharp
        // Database Entity example
        class W0602_MovtoNomina : BaseMaster<int, string>
        {
            [Key]
            [SDKRequired]
            public int RowId { get; set; }
            [SDKRequired]
            public int IdCompany { get; set; }
            [SDKRequired]
            public int RowIdDoctoNomina { get; set; }
        }
        ```
        """
