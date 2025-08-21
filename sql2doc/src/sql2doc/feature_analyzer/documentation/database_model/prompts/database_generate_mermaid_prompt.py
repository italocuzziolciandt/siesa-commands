from feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


class DatabaseGenerateMermaidPrompt(AnalyzerPrompt):
    def __init__(self, feature_database_full_content: str) -> None:
        self.feature_database_full_content = feature_database_full_content

    def get_system_message(self) -> str:
        return """
        You are a Database Architect specializing in reverse-engineering database schemas from SQL code. Your objective is to analyze multiple Mermaid ER diagrams representing database structures extracted from SQL stored procedures and consolidate them into a single, comprehensive diagram. You pay close attention to detail and prioritize accuracy and completeness.

        Your Role:
        **Diagram Analysis:** Analyze individual Mermaid ER diagrams to identify tables, columns, and relationships.
        **Duplicate Detection:** Identify and resolve duplicate tables and relationships across multiple diagrams.
        **Schema Consolidation:** Combine individual diagrams into a single, unified diagram, ensuring that all tables and relationships are accurately represented.
        **Detail Preservation:** Preserve all relevant details about tables and columns, including data types, sizes, and relationships.
        **Clarity and Conciseness:** Create clear and concise diagrams that are easy to understand and maintain.
        **SQL Awareness:** Understand SQL syntax and semantics to accurately interpret table and relationship definitions.

        Prioritize:
        **Accuracy:** Ensure that the consolidated diagram accurately reflects the database structure represented in the individual diagrams.
        **Completeness:** Include all tables, columns, and relationships that are present in the individual diagrams.
        **Clarity:** Create a diagram that is easy to understand and navigate.

        Ignore:
        - Performance optimizations
        - Code style details

        Mermaid syntax for ER diagrams is compatible with PlantUML, with an extension to label the relationship. 
        Each statement consists of the following parts:
        ```<first-entity> [<relationship> <second-entity> : <relationship-label>]```

        Where:
        - first-entity is the name of an entity. Names support any unicode characters and can include spaces if surrounded by double quotes (e.g. "name with space").
        - relationship describes the way that both entities inter-relate. See below.
        - second-entity is the name of the other entity.
        - relationship-label describes the relationship from the perspective of the first entity.

        For example:
        ```PROPERTY ||--|{ ROOM : contains```     
        """

    def get_user_message(self) -> str:
        return f"""
        Considering the SQL code below:
        ```markdown
        {self.feature_database_full_content}
        ```

        Generate a Mermaid ER diagram representing the database structure used by this code. 

        Here you have some examples on how to represent the database structure:
        {self.__get_few_shots_examples()}

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

    def __get_few_shots_examples(self) -> str:
        return """
        erDiagram
            CAR ||--o{ NAMED-DRIVER : allows
            CAR {
                string registrationNumber PK
                string make
                string model
                string[] parts
            }
            PERSON ||--o{ NAMED-DRIVER : is
            PERSON {
                string driversLicense PK "The license #"
                string(99) firstName "Only 99 characters are allowed"
                string lastName
                string phone UK
                int age
            }
            NAMED-DRIVER {
                string carRegistrationNumber PK, FK
                string driverLicence PK, FK
            }
            MANUFACTURER only one to zero or more CAR : makes   
        ----
        erDiagram
            direction LR
            CUSTOMER ||--o{ ORDER : places
            CUSTOMER {
                string name
                string custNumber
                string sector
            }
            ORDER ||--|{ LINE-ITEM : contains
            ORDER {
                int orderNumber
                string deliveryAddress
            }
            LINE-ITEM {
                string productCode
                int quantity
                float pricePerUnit
            }
        ----
        erDiagram
            CAR {
                string registrationNumber
                string make
                string model
            }
            PERSON {
                string firstName
                string lastName
                int age
            }
            PERSON:::foo ||--|| CAR : owns
            PERSON o{--|| HOUSE:::bar : has
        ----
        erDiagram
            CUSTOMER }|..|{ DELIVERY-ADDRESS : has
            CUSTOMER ||--o{ ORDER : places
            CUSTOMER ||--o{ INVOICE : "liable for"
            DELIVERY-ADDRESS ||--o{ ORDER : receives
            INVOICE ||--|{ ORDER : covers
            ORDER ||--|{ ORDER-ITEM : includes
            PRODUCT-CATEGORY ||--|{ PRODUCT : contains
            PRODUCT ||--o{ ORDER-ITEM : "ordered in"
        """