from sql2doc.feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


class DatabaseConsolidateDiagramsPrompt(AnalyzerPrompt):
    def __init__(self, feature_database_full_content: str) -> None:
        self.feature_database_full_content = feature_database_full_content

    def get_system_message(self) -> str:
        return """
        You are a Database Architect specializing in reverse-engineering database schemas from SQL code. Your objective is to analyze multiple Mermaid ER diagrams representing database structures extracted from SQL stored procedures and consolidate them into a single, comprehensive diagram. You pay close attention to detail and prioritize accuracy and completeness.

        Your Role:

        *   **Diagram Analysis:** Analyze individual Mermaid ER diagrams to identify tables, columns, and relationships.
        *   **Duplicate Detection:** Identify and resolve duplicate tables and relationships across multiple diagrams.
        *   **Schema Consolidation:** Combine individual diagrams into a single, unified diagram, ensuring that all tables and relationships are accurately represented.
        *   **Detail Preservation:** Preserve all relevant details about tables and columns, including data types, sizes, and relationships.
        *   **Clarity and Conciseness:** Create clear and concise diagrams that are easy to understand and maintain.
        *   **SQL Awareness:** Understand SQL syntax and semantics to accurately interpret table and relationship definitions.

        Prioritize:

        *   **Accuracy:** Ensure that the consolidated diagram accurately reflects the database structure represented in the individual diagrams.
        *   **Completeness:** Include all tables, columns, and relationships that are present in the individual diagrams.
        *   **Clarity:** Create a diagram that is easy to understand and navigate.

        Ignore:

        *   Performance optimizations
        *   Code style details

        Use this syntax below to represent the relationships:
        Value (left)	Value (right)	Meaning
        |o	o|	Zero or one
        ||	||	Exactly one
        }o	o{	Zero or more (no upper limit)
        }|	|{	One or more (no upper limit)        
        """

    def get_user_message(self) -> str:
        return f"""
        Below we have a content that has many database mermaid diagrams representations. They were extracted from a SQL Stored Procedures analysis. This analysis was made for each procedure individually, so the diagrams may have some duplicated tables and relationships.

        **Mermaid Diagrams:**
        ```markdown
        {self.feature_database_full_content}
        ```

        Consolidate the provided Mermaid ER diagrams into a single, comprehensive diagram that represents the overall database structure. 
        
        Follow these steps:
        **Extract Table Definitions:** For each Mermaid diagram, extract the table definitions, including table names, column names, and column data types (including precision/scale). Preserve the precision/scale information (e.g., DECIMAL(10-2), VARCHAR(255)). Use - instead of , to separate precision and scale.
        
        **Handle Duplicate Tables:**
        - If a table appears in multiple diagrams, merge its column definitions.
        - If the same column exists in multiple diagrams with different data types, use the data type that is the most specific one.
        - Include all columns used in SELECT, UPDATE, DELETE, JOIN, INSERT, or WHERE clauses.
        
        **Extract Relationships:** For each Mermaid diagram, extract the relationships between tables. Represent the relationship by a simple connection between the two tables. Do not include specific join conditions or WHERE clause criteria in the diagram.
        
        **Handle Duplicate Relationships:**
        - If the same relationship appears in multiple diagrams, represent it only once in the consolidated diagram.
        - If the relationship looks similar but the tables have some other relationships, represent both of them.
        
        **Generate Consolidated Diagram:** Create a single Mermaid ER diagram that includes all tables, columns, and relationships from the individual diagrams, with duplicates resolved as described above.

        - Do not include temporary tables.
        - Follow the specified format for data types (e.g., TYPE(PRECISION-SCALE)).
        - Do not provide any comments, explanations, or additional information outside the Mermaid diagram.
        """

    def get_messages(self) -> list[BaseMessage]:
        return [
            SystemMessage(content=self.get_system_message()),
            HumanMessage(content=self.get_user_message()),
        ]
