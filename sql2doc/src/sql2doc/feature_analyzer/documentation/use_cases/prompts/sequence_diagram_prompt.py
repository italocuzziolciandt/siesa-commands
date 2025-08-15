from sql2doc.feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


class SequenceDiagramPrompt(AnalyzerPrompt):
    def __init__(
        self,
        use_cases_content: str,
    ) -> None:
        self.use_cases_content = use_cases_content

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
        Considering a set of Use Cases that represent a **business process**, provide a mermaid sequence diagram that illustrates the interactions between actors and the system. As the Use Cases represent a business process, the sequence diagram should reflect the overall flow of the process, including decision points and alternative paths.

        **Use Cases:**
        ```markdown
            {self.use_cases_content}
        ```

        Here a simple example of a sequence diagram:
        ```mermaid
            sequenceDiagram
                actor Alice
                actor Bob
                Alice->>Bob: Hi Bob
                Bob->>Alice: Hi Alice
        ```

        Important:
        - Don't provide any explanations or additional text outside the Mermaid diagrams.
        - Don't make assumptions about the business context that are not directly supported by the T-SQL code.
        """

    def get_messages(self) -> list[BaseMessage]:
        return [
            SystemMessage(content=self.get_system_message()),
            HumanMessage(content=self.get_user_message()),
        ]
