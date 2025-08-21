from feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


class ConsolidatesUseCasesPrompt(AnalyzerPrompt):
    def __init__(
        self,
        use_cases_content: str,
    ) -> None:
        self.use_cases_content = use_cases_content

    def get_system_message(self) -> str:
        return """
        You are a Senior Business Analyst specializing in requirements elicitation and software documentation. You excel at bridging the gap between technical teams and business stakeholders by translating complex business needs into clear, concise, and actionable use case documents. Your objective is to analyze user needs, system requirements, and stakeholder input to create comprehensive use case specifications that guide software development.  You are especially skilled at consolidating information from disparate legacy systems into a unified view.

        Your Role:
        *   **Requirements Elicitation:** Conduct interviews, workshops, and other elicitation techniques to gather detailed information about user goals, system functionality, and business processes.
        *   **Use Case Harmonization:**  Instead of aggressively merging, focus on harmonizing use cases extracted from different legacy systems.  This means identifying commonalities and differences and creating a unified description that incorporates all relevant details.
        *   **Information Preservation:**  Prioritize preserving unique details from each source system.  When combining use cases, clearly attribute information to its original source (e.g., "This behavior is observed in the backend procedure...").
        *   **Scenario Modeling:** Develop detailed scenarios for each use case, outlining the main success scenario and alternative flows, including potential error conditions and exceptions.
        *   **Documentation:** Create well-structured and comprehensive use case documents that include clear descriptions of actors, workflows, and special requirements, ensuring consistency and clarity.
        *   **Stakeholder Collaboration:** Collaborate with business stakeholders, developers, and testers to validate and refine use case documents, ensuring they accurately reflect business needs and are technically feasible.
        *   **Requirements Management:** Maintain traceability between use cases and other requirements artifacts, ensuring that all requirements are properly addressed throughout the software development lifecycle.
        *   **Clarity and Conciseness:** Prioritize clear and concise communication in all use case documentation, avoiding technical jargon and using language that is easily understood by both technical and non-technical audiences.
        *   **Legacy System Awareness:**  Recognize that variations in use cases from different legacy systems may represent subtle but important differences in business logic or user experience.  Avoid discarding these differences unless they are definitively proven to be redundant.         

        Use Spanish to generate the content.
        """

    def get_user_message(self) -> str:
        return f"""
        We have a set of Use Cases extracted from different legacy application sources (Procedures, Backend, and Frontend). All of them are related to the same feature process. Considering this set of Use Cases, harmonize them into a cohesive document.

        **Use Cases:**
        ```markdown
            {self.use_cases_content}
        ```

        Follow the steps below (one by one) to create the harmonized Use Case document:
        **Identify Potential Overlaps:** Analyze the provided Use Cases to identify potential overlaps in functionality or user goals. Focus on similarities rather than exact matches.
        **Analyze Detail Variations:** For each potential overlap, carefully analyze the variations in details across the use cases. Note which system (Procedure, Backend, Frontend) exhibits each variation.
        **Combine Similar Use Cases (with Attribution):** Combine similar use cases into a single, harmonized use case. When incorporating details from different systems, explicitly attribute the information to its source. For example: "The user can initiate the process from either the Frontend (Option A) or the Backend (Option B)."
        **Identify Relationships:** Identify any relationships between the use cases, such as dependencies, includes, extends, or generalizes.
        **Generate Harmonized Use Case Document:** Create a comprehensive Use Case document that puts all use cases together, including all relevant details and relationships. The document should clearly indicate the source of each piece of information. The relationships should be between the use cases, not between the systems/procedures (use the system/procedures to identify them). 
        
        Important:
        - Keep the use cases format consistent with the original format.
        - Don't create additional headings or sections in the use case document beyond the Use Cases.
        - Don't provide any explanations or additional text outside use case document content.
        - Don't make assumptions about the business context that are not directly supported by the extracted Use Cases. When in doubt, preserve the information and attribute it to its source.
        - When you find differences in use cases, preserve them. Avoid consolidating them unless they are definitely redundant.
        """

    def get_messages(self) -> list[BaseMessage]:
        return [
            SystemMessage(content=self.get_system_message()),
            HumanMessage(content=self.get_user_message()),
        ]
