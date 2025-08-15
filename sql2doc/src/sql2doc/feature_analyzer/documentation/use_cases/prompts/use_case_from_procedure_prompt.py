from sql2doc.feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from sql2doc.feature_analyzer.documentation.use_cases.prompts.use_case_document_template import (
    use_case_document_template,
)


class UseCasesFromProcedurePrompt(AnalyzerPrompt):
    def __init__(
        self,
        procedure_name: str,
        procedure_content: str,
    ) -> None:
        self.procedure_name = procedure_name
        self.procedure_content = procedure_content

    def get_system_message(self) -> str:
        return """
        You are a Senior Business Analyst specializing in requirements elicitation and software documentation. You excel at bridging the gap between technical teams and business stakeholders by translating complex business needs into clear, concise, and actionable use case documents. Your objective is to analyze user needs, system requirements, and stakeholder input to create comprehensive use case specifications that guide software development.

        Your Role:
        -   **Requirements Elicitation:** Conduct interviews, workshops, and other elicitation techniques to gather detailed information about user goals, system functionality, and business processes.
        -   **Use Case Identification:** Identify and define distinct use cases based on the collected requirements, focusing on the interactions between actors and the system to achieve specific goals.
        -   **Scenario Modeling:** Develop detailed scenarios for each use case, outlining the main success scenario and alternative flows, including potential error conditions and exceptions.
        -   **Documentation:** Create well-structured and comprehensive use case documents that include clear descriptions of actors, preconditions, postconditions, workflows, and special requirements, ensuring consistency and clarity.
        -   **Stakeholder Collaboration:** Collaborate with business stakeholders, developers, and testers to validate and refine use case documents, ensuring they accurately reflect business needs and are technically feasible.
        -   **Requirements Management:** Maintain traceability between use cases and other requirements artifacts, ensuring that all requirements are properly addressed throughout the software development lifecycle.
        -   **Clarity and Conciseness:** Prioritize clear and concise communication in all use case documentation, avoiding technical jargon and using language that is easily understood by both technical and non-technical audiences. 

        Use Spanish to generate the content.
        """

    def get_user_message(self) -> str:
        return f"""
        Analyze the following T-SQL stored procedure and generate a detailed Use Case document based on the template. Focus on identifying the core business function it performs, the actors involved (either directly or indirectly), the preconditions required for successful execution, the expected outcomes (success and failure), and the steps involved in both the main success scenario and any relevant alternative flows. Pay close attention to any performance, security, or data integrity considerations that should be highlighted as special requirements.

        **T-SQL Stored Procedure:**
        ```sql
            {self.procedure_content}
        ```

        Strictly follow the steps below (one by one) to create the Use Case document:
        1. **Identify the Use Cases:** Analyze the stored procedure to identify distinct use cases it supports.
        2. **Describe the Use Cases:** For each identified use case, fill out the Use Case following the provided template.

        Use Case Template:
        {use_case_document_template}

        Important:
        - Replace the [ ... ] placeholders in the template with the appropriate details derived from the T-SQL stored procedure.
        - Focus on the business logic implied by the code, not just the technical implementation.
        - Provide clear and concise descriptions for each section of the use case document.
        - Don't provide any explanations or additional text outside the Mermaid diagrams.
        - Don't make assumptions about the business context that are not directly supported by the T-SQL code.
        """

    def get_messages(self) -> list[BaseMessage]:
        return [
            SystemMessage(content=self.get_system_message()),
            HumanMessage(content=self.get_user_message()),
        ]
