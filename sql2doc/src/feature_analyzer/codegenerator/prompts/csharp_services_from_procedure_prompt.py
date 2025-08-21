from feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


class CSharpServicesFromProcedurePrompt(AnalyzerPrompt):
    def __init__(
        self,
        procedure_name: str,
        procedure_content: str,
        procedure_mermaid_representation: str,
        class_to_be_implemented: str,
        parent_class_content: str = "",
        repositories_interface_content: str = "",
    ) -> None:
        self.procedure_name = procedure_name
        self.procedure_content = procedure_content
        self.procedure_mermaid_representation = procedure_mermaid_representation
        self.class_to_be_implemented = class_to_be_implemented
        self.parent_class_content = (parent_class_content,)
        self.repositories_interface_content = repositories_interface_content

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
            We are modernizing an legacy application from Java to .NET C#. The application is composed by a backend (java) and a database (Transact-SQL).
            To modernize the legacy application from Java to .NET C#, we will create a new application that modernizes the functionality of the existing stored procedure `{self.procedure_name}`.

            For the new application, we need to generate the Service Layer (Business Logic). The Service Layer (Business Logic) is responsible for implementing all the procedure business logic. The repository layer is already implemented, so you don't need to worry about it.

            This is the stored procedure that needs to be modernized:
            ```sql
            {self.procedure_content}
            ```

            Based on the context above, provide the implementation for the Data Access Layer (Repository) in the new application, that represents and modernizes the tables interactions in the existing sql stored procedure. Pay attention on optimizing the business logic implementations.

            {
                f"""Here we have the available repositories that can be used in the Service Layer:
                ```csharp
                {self.repositories_interface_content}
                ```
                """
                if self.repositories_interface_content else ""
            }

            {
                f"The class to be implemented is {self.class_to_be_implemented}.\n\n" 
                if self.class_to_be_implemented else ""
            }
            {
                f"Here is the content of the parent class that execute the `{self.class_to_be_implemented}`:\n\n{self.parent_class_content}\n\n" 
                if self.parent_class_content else ""
            }

            Coding Guidelines:
            - Follow SOLID principles and design patterns.
            - Use the available repositories for database operations.
            - Use dependency injection for better testability (create interfaces for your services).
            - Avoid on using static methods unless absolutely necessary.
            - Use the best practices on .NET C# coding, such as naming conventions, code structure, and error handling.

            Provide a **complete class implementation** for all services, without summarizing or truncating the response. If the response exceeds the max output limit, continue generating until all services are fully covered.

            A service represent the business logic of the current Stored Procedure. Stored Procedures called by the current one, should be mapped as dependency implementation.
            Ignore imports and namespaces, just provide the class implementation.
            Always start implementation at the lowest layer of the application.
            Don't generate the Repository Layer, use as assumption that this layer is already implemented.
            Don't make assumptions, provide the full implementation of the necessary classes and methods.
            Don't add any additional comments or explanations, just provide the code implementation.

            Crucial: Ensure that the generated code is fully compilable. All methods must have complete implementations, even if some logic is initially basic or incomplete.
        """

    def get_messages(self) -> list[BaseMessage]:
        return [
            SystemMessage(content=self.get_system_message()),
            HumanMessage(content=self.get_user_message()),
        ]
