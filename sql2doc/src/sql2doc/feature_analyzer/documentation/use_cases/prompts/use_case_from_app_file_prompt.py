from sql2doc.feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from sql2doc.feature_analyzer.documentation.use_cases.prompts.use_case_document_template import (
    use_case_document_template,
)


class UseCasesFromApplicationFilePrompt(AnalyzerPrompt):
    def __init__(
        self,
        file_name: str,
        file_content: str,
        method_names: list[str] = None,
    ) -> None:
        self.file_name = file_name
        self.file_content = file_content
        self.method_names = method_names

    def get_system_message(self) -> str:
        return """
        You are a Full Stack Developer (Java, JavaScript, SQL) analyzing code for modernization documentation. Focus on features, not performance or code structure.

        **Task:** Analyze provided code files to identify:
        *   **Features & User Stories:** What can users *do*?
        *   **Feature Dependencies:** Which features rely on others?
        *   **Data Flow:** Where does data come from and go?
        *   **UI/UX:** Key UI elements and user interactions.
        *   **Business Logic:** Core rules and validations.
        *   **External Integrations:** Which APIs are used?
        *   **Configuration Points:** How can features be configured?

        **Prioritize:** Feature understanding, user perspective, high-level functionality.
        **Ignore:** Performance optimizations, code style details.
        **Deliverable:** A summary of each feature, including functionality, user stories, data flow, UI/UX, business logic, dependencies, integrations, and configuration options.

        Clarify assumptions. Ask questions if needed. Only answer if you have knowledge about the subject. If you don't have knowledge about it, ask for more information, provide some questions that the user can answer providing more context to you or as last resort, answer "Sorry, I don't have enough knowledge about the subject.

        Use Spanish to generate the content.
        """

    def get_user_message(self) -> str:
        return f"""
        Analyze the following application file and generate a detailed Use Case document based on the template. Focus on identifying the core business function it performs, the actors involved (either directly or indirectly), the preconditions required for successful execution, the expected outcomes (success and failure), and the steps involved in both the main success scenario and any relevant alternative flows. Pay close attention to any performance, security, or data integrity considerations that should be highlighted as special requirements.

        **Application File:**
        ```sql
            {self.file_name}
            {self.file_content}
        ```

        Strictly follow the steps below (one by one) to create the Use Case document:
        1. **Identify the Use Cases:** Analyze the appplication file to identify distinct use cases it supports.
        2. **Describe the Use Cases:** For each identified use case, fill out the Use Case following the provided template.

        Use Case Template:
        {use_case_document_template}

        {
            f"You should focus only in the following methods and their respective call stacks: {', '.join(self.method_names)}" if self.method_names is not None else ""
        }

        Important:
        - Replace the [ ... ] placeholders in the template with the appropriate details derived from the application file.
        - Focus on the business logic implied by the code, not just the technical implementation.
        - Provide clear and concise descriptions for each section of the use case document.
        - Don't provide any explanations or additional text outside the Mermaid diagrams.
        - Don't make assumptions about the business context that are not directly supported by the application file.
        """

    def get_messages(self) -> list[BaseMessage]:
        return [
            SystemMessage(content=self.get_system_message()),
            HumanMessage(content=self.get_user_message()),
        ]
