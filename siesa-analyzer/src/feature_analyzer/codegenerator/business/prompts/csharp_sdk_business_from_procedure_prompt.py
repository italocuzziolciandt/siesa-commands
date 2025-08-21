from feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


class CSharpSDKBusinessFromProcedurePrompt(AnalyzerPrompt):
    def __init__(
        self,
        procedure_name: str,
        procedure_content: str,
        procedure_mermaid_representation: str,
        class_to_be_implemented: str,
        parent_class_content: str = "",
    ) -> None:
        self.procedure_name = procedure_name
        self.procedure_content = procedure_content
        self.procedure_mermaid_representation = procedure_mermaid_representation
        self.class_to_be_implemented = class_to_be_implemented
        self.parent_class_content = parent_class_content

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
            To modernize the legacy application, we will create a new application that modernizes the functionality of the existing stored procedure `{self.procedure_name}`.

            For the new application, we need to generate the Business Layer. The Business Layer is responsible for implementing all the procedure business logic.

            This is the stored procedure that needs to be modernized:
            ```sql
            {self.procedure_content}
            ```

            Provide the implementation for the Business Layer of the new application, that represents and modernizes the business logic in the sql stored procedure. Pay attention on optimizing the business logic implementations instead of just translating the SQL logic to C# code.

            {
                f"The class to be implemented is {self.class_to_be_implemented}.\n\n" 
                if self.class_to_be_implemented else ""
            }
            {
                f"Here is the content of the parent class that execute the `{self.class_to_be_implemented}`:\n\n{self.parent_class_content}\n\n" 
                if self.parent_class_content else ""
            }

            {self.__get_code_guidelines()}

            {self.__get_name_conventions()}

            Follow the example of the Business Layer implementation:
            {self.__get_business_layer_example()}

            Provide a **complete class implementation** for all business classes, without summarizing or truncating the response. If the response exceeds the max output limit, continue generating until all business classes are fully covered.

            Important:
            - Consider that the supporting classes, interfaces and attributes are already implemented, don't worry about compilable code related to them.
            - If you already have a object with the data, don't create variables to store the same data from the object, just use the object directly.
            - Ignore Auditing and Logging implemented in the legacy application SQL Stored Procedure.
            - Ignore imports and namespaces, just provide the class implementation and interface definitions.
            - Don't implement the entities, use as assumption the tables and columns names in Pascal Case.
            - Don't make assumptions or truncate the implementation, provide the full implementation of the necessary class methods.
            - Don't add comments or explanations, just provide the code implementation.

            Crucial: Ensure that the generated code is fully compilable. All methods must have complete implementations, even if some logic is initially basic or incomplete.
        """

    def get_messages(self) -> list[BaseMessage]:
        return [
            SystemMessage(content=self.get_system_message()),
            HumanMessage(content=self.get_user_message()),
        ]

    def __get_code_guidelines(self) -> str:
        return """
            Coding Guidelines:
            - Follow SOLID principles and design patterns.
            - This architecture access the DbContext directly, so it is not necessary to use repositories.
            - Use dependency injection for better testability (create interfaces for your classes).
            - Avoid on using static methods unless absolutely necessary.
            - Use the best practices on .NET C# coding, such as naming conventions, code structure, and error handling.
            - Split the class implementation steps in multiple methods, to keep the code clean and maintainable.
        """

    def __get_name_conventions(self) -> str:
        return """
            Name Conventions:
            - Class Names: Use PascalCase (e.g., UserController, ProductService). Each word starts with a capital letter, and no underscores or hyphens are used.
            - Method Names:
                - Use English.
                - Use verbs that describe the action the method performs.
                - Use PascalCase (e.g., GetUserById).
            - Descriptive Names: Names should be descriptive and clearly reflect their purpose.
            - Model Names: Defined with an initial letter describing their role, followed by a 5-digit code. The first two digits define the service code, and the rest are a unique code (e.g., E30010_Client).
            - Model Properties: Use PascalCase (e.g., Rowid, Id, Subdomain).
            Business Logic Directories: Named with the model name prefixed by the code "BL" (e.g., BLClient).
        """

    def __get_business_layer_example(self) -> str:
        return """
        ```csharp
        // Business Logic Layer example
        // For Business Service that is not responsible for CRUD operations for specific table, use BLBackendSimple like: `class BLNominaLiquidBasicos : BLBackendSimple`
        class BLNominaLiquidBasicos : BLBackendSimple<W0602MovtoNomina, BLBaseValidator<W0602MovtoNomina>>
        {
            public BLNominaLiquidBasicos(IAuthetenticationService authenticationService) : base(authenticationService) { }

            [SDKExposedMethod]
            public async Task<ActionResult> LiquidBasicosYTNL(int pIdLenguaje, int pRowIdUsuario, int pRowIdDocto, byte pIndIndividual)
            {
                try
                {
                    await using var context = CreateDbContext();

                    // Implement the logic to liquidate the basic YTNL for the given id

                    return new ActionResult() { Success = true, Data = "Successfully liquidated basic YTNL." };
                }
                catch (Exception ex)
                {
                    return new ActionResult() { Success = false, Errors = new List<string> { ex.Message } };
                }
            }
        }
        ```
        """
