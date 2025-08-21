from feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


class DatabaseConsolidateDiagramsPrompt(AnalyzerPrompt):
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
        return f""""
        Below is a collection of Mermaid ER diagrams extracted from the analysis of individual SQL Stored Procedures. Because the analysis was done procedure-by-procedure, many tables and relationships are duplicated across the diagrams.

        **Mermaid Diagrams:**
        ```markdown
        {self.feature_database_full_content}

        Your task is to consolidate the provided Mermaid ER diagrams into a single, comprehensive diagram that represents the overall database structure accurately and cleanly.

        Follow these steps meticulously:
        1. Extract Table Definitions
        - From each Mermaid diagram, extract all table definitions, including table names, column names, and their data types.
        - Crucially, preserve the precision and scale for data types like DECIMAL or VARCHAR. Use a hyphen to separate precision and scale as specified (e.g., DECIMAL(10-2), VARCHAR(255)).

        2. Handle Duplicate Tables
        - If a table appears in multiple diagrams, merge its column definitions into a single entity.
        - If the same column appears with different data types, choose the most specific or largest type to ensure compatibility (e.g., prefer VARCHAR(100) over VARCHAR(50)).
        - The final table definition should include every unique column found across all diagrams for that table.

        3. Unify and Consolidate Relationships
        - The primary goal is to represent only one relationship for any given pair of tables, even if they are linked with different labels in the source diagrams.
        - Identify all unique pairs of connected tables (e.g., TableA and TableB).
        - For each pair, gather all the different relationship labels found in the source diagrams (e.g., "references", "created_by", "has_type").

        Synthesize these labels into a single, generic, and descriptive name that best captures the essence of the connection. Avoid overly specific labels from a single context.

        Represent this unified relationship only once in the final diagram.

        Example of Consolidation:
        - If you find the following relationships between w0550_contratos and w0510_grupos_empleados:
        w0550_contratos ||--o{{ w0510_grupos_empleados : belongs_to
        w0550_contratos ||--o{{ w0510_grupos_empleados : has
        w0550_contratos ||--o{{ w0510_grupos_empleados : relates

        You must consolidate them into a single relationship with a generic label. A good choice would be relates_to or has_group. The final output should be just one line:
        w0550_contratos ||--o{{ w0510_grupos_empleados : relates_to

        4. Generate Consolidated Diagram
        Create a single Mermaid ER diagram that includes all unique tables with their complete column sets and the unified relationships.

        Ensure the output is only the final, clean Mermaid code block.

        Here are some examples of the expected output format:
        {self.__get_few_shots_examples()}

        Constraints:
        - Do not include temporary tables (e.g., tables starting with # or @).
        - Strictly follow the specified format for data types: TYPE(PRECISION-SCALE).
        - The output must consist **only** of the complete erDiagramcode block. Do not add any comments (e.g.,-- Relationships), explanations, or introductory text, either inside or outside the diagram code.
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
