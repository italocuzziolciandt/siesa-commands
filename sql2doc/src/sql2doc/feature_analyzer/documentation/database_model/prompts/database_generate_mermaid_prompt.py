from sql2doc.feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


class DatabaseGenerateMermaidPrompt(AnalyzerPrompt):
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
        Considering the SQL code below:
        ```markdown
        {self.feature_database_full_content}
        ```

        Generate a Mermaid ER diagram representing the database structure used by this code. 
        
        Follow these guidelines:
        **Table Inclusion:** Include all tables used in the following SQL clauses: SELECT, UPDATE, DELETE, JOIN, INSERT, and WHERE. Do not include temporary tables.

        **Column Inclusion:** For each table, include only the columns that are explicitly referenced in the SQL code. This includes columns used in SELECT, WHERE, JOIN, UPDATE, and INSERT clauses. If a SELECT * is used, include all columns from that table.

        **Relationship Representation:** Represent relationships between tables with a simple connection line. Do not include the specific join conditions or WHERE clause criteria in the diagram. Focus on the existence of a relationship, not its details.

        **Data Type Formatting:** For column data types that include precision and scale, use the format TYPE(PRECISION-SCALE) (e.g., DECIMAL(10-2), VARCHAR(255)). Use a hyphen (-) to separate precision and scale, not a comma.

        **Precision and Scale Defaults:** If the column is defined with a precision and scale, always provide the scale. If the scale is 0, write the type as DECIMAL(PRECISION-0).

        **Conciseness:** Only include the Mermaid diagram code. Do not include any additional text, explanations, or comments.
        """

    def get_messages(self) -> list[BaseMessage]:
        return [
            SystemMessage(content=self.get_system_message()),
            HumanMessage(content=self.get_user_message()),
        ]
