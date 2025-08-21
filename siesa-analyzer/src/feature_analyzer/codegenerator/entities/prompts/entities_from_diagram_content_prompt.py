from feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


from feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


class EntitiesFromDiagramContentPrompt(AnalyzerPrompt):
    def __init__(
        self,
        database_model_diagram: str,
    ) -> None:
        self.database_model_diagram = database_model_diagram

    def get_system_message(self) -> str:
        return """
        You are an expert C# and Entity Framework architect. Your task is to translate a Mermaid database diagram into a complete set of C# Entity Framework Core classes. You must follow all coding guidelines and formatting instructions with extreme precision. Your output must be only the C# code as requested.
        """

    def get_user_message(self) -> str:
        return f"""
        We are generating C# Entity Framework Core entities from a database model for a .NET modernization project.

        This is the database model diagram:
        ```mermaid
        {self.database_model_diagram}
        ```

        ## OUTPUT FORMAT
        Your output **must** be a single block of C# code. You **must** wrap each entity class (including its `using` statements) within unique start and end delimiters. This is critical for automated file splitting.
        Use the following format for each entity:

        ```csharp
        // START_ENTITY_FILE: EntityName.cs
        using ...;
        // ... other usings

        public class EntityName : BaseMaster<...>
        {{
            // properties and relationships
        }}
        // END_ENTITY_FILE
        ```

        ## CODING GUIDELINES
        You **must** adhere to the following rules for every entity you generate:

        1.  **One Class Per Table:** Generate one C# entity class for each table defined in the Mermaid diagram.
        2.  **Inheritance:** All entities **must** inherit from `BaseMaster<T, U>`. The generic types `T` and `U` should be inferred from the primary key type.
        3.  **Base Properties:** **Do not** redefine properties that already exist in the provided base classes (`BaseMaster`, `BaseAudit`). This includes audit fields like `CreationDate`, `LastUpdateDate`, and master fields like `Id`, `Name`, `Description`, and `Status`.
        4.  **Naming Convention:**
            - For table `TableName`, the entity class name **must** be `E<SERVICE_CODE>_<UNIQUE_CODE>_TableName`.
            - Since the service and unique codes are unknown, use placeholders: `EXX` for `<SERVICE_CODE>` and a sequential number for `<UNIQUE_CODE>`, starting from `001`.
            - For example: for tables `Client` and `Product`, the classes will be `EXX001_Client` and `EXX002_Product`.
        5.  **Annotations:** Use the following annotations where appropriate:
            - `[SDKRequired]`: For all non-nullable database columns.
            - `[SDKStringLength(size)]`: For `varchar` or `string` properties to define their max length.
            - `[ForeignKey("PropertyName")]`: To define navigation properties for foreign key relationships.
        6.  **Required Strings:** Add the `required` modifier to all `string` properties that are not nullable in the database.
        7.  **Relationships:** Implement all foreign key relationships shown in the diagram as navigation properties.
        8.  **Completeness:** Provide the **full, complete, and unabridged C# code** for all entities. Do not use comments like "// ... other properties" or truncate any part of the code.
        9.  **No Explanations:** The output **must not** contain any explanations, comments, or text other than the C# code and the required delimiters.

        ## REFERENCE MATERIALS

        ### Base Class Definitions:
        {self.__get_base_classes_definitions()}

        ### Correct Entity Example:
        {self.__get_entity_example()}
        """

    def get_messages(self) -> list[BaseMessage]:
        return [
            SystemMessage(content=self.get_system_message()),
            HumanMessage(content=self.get_user_message()),
        ]

    def __get_base_classes_definitions(self) -> str:
        # No changes needed here, the original was good.
        return """
        ```csharp
        // ... (original base class code) ...
        using System;
        using System.Collections.Generic;
        using System.ComponentModel.DataAnnotations.Schema;
        using System.Runtime.InteropServices;
        using Siesa.Global.Enums;
        using Siesa.SDK.Shared.DataAnnotations;

        namespace Siesa.SDK.Entities;

        public abstract class BaseAudit<T> : BaseSDK<T>
        {
            [SDKImportExclude]
            [Column(Order = 3)]
            [SDKRequired]
            public virtual DateTime CreationDate { get; set; } = DateTime.UtcNow;

            [SDKImportExclude]
            [Column(Order = 4)]
            public virtual DateTime? LastUpdateDate { get; set; } = DateTime.UtcNow;

            [SDKImportExclude]
            [Column(Order = 5)]
            [SDKStringLength(2000)]
            public virtual string? Source { get; set; }

            [SDKImportExclude]
            [Column(Order = 6)]
            [SDKRequired]
            public virtual int RowidUserCreates { get; set; }

            [SDKImportExclude]
            [Column(Order = 7)]
            public virtual int? RowidUserLastUpdate { get; set; }

            [SDKFlexExclude(true)]
            [SDKImportExclude]
            [Column(Order = 9)]
            public virtual int? RowidSession { get; set; }

            [SDKImportExclude]
            [Column(Order = 8)]
            public virtual int? RowidUserOwner { get; set; }

            [ForeignKey("RowidUserLastUpdate")]
            public virtual E00220_User? UserLastUpdate { get; set; }

            [ForeignKey("RowidUserOwner")]
            public virtual E00220_User? UserOwner { get; set; }

            [ForeignKey("RowidUserCreates")]
            public virtual E00220_User UserCreates { get; set; }
        }

        public abstract class BaseMaster<T, U> : BaseAudit<T>
        {
            [Column(Order = 10)]
            public virtual U Id { get; set; }

            [Column(Order = 11)]
            [SDKRequired]
            [SDKStringLength(250)]
            public virtual string Name { get; set; } = string.Empty;

            [Column(Order = 12)]
            [SDKStringLength(2000)]
            public virtual string? Description { get; set; }

            [Column(Order = 13)]
            [SDKRequired]
            public virtual EnumStatusBaseMaster Status { get; set; }

            [Column(Order = 14)]
            [SDKRequired]
            public virtual bool IsPrivate { get; set; }

            [SDKFlexExclude(true)]
            [Column(Order = 15)]
            public virtual int? RowidAttachment { get; set; }

            [ForeignKey("RowidAttachment")]
            public virtual E00270_Attachment? Attachment { get; set; }

            [NotMapped]
            public static string ToStringTemplate { get; } = "({0}) - {1}";

            [NotMapped]
            public static List<string> ToStringProperties { get; }

            public override string ToString()
            {
                return $"({Id}) - {Name}";
            }

            static BaseMaster()
            {
                int num = 2;
                List<string> list = new List<string>(num);
                CollectionsMarshal.SetCount(list, num);
                Span<string> span = CollectionsMarshal.AsSpan(list);
                int num2 = 0;
                span[num2] = "Id";
                num2++;
                span[num2] = "Name";
                num2++;
                ToStringProperties = list;
            }
        }
        ```
        """

    def __get_entity_example(self) -> str:
        return """
        ```csharp
        // START_ENTITY_FILE: EXX001_PayrollMovement.cs
        using System.ComponentModel.DataAnnotations;
        using System.ComponentModel.DataAnnotations.Schema;
        using Siesa.SDK.Entities;
        using Siesa.SDK.Shared.DataAnnotations;

        /// <summary>
        /// Represents a payroll movement (or transaction) within the system.
        /// </summary>
        public class EXX001_PayrollMovement : BaseMaster<int, string>
        {
            [SDKIdentity]
            [Key]
            [SDKRequired]
            public int RowId { get; set; }

            [SDKRequired]
            public int IdCompany { get; set; }
            
            [SDKRequired]
            public int RowidInternalUser { get; set; }

            [ForeignKey("RowidInternalUser")]
            public virtual E00220_User? InternalUser { get; set; }

            [SDKStringLength(255)]
            public string? Notes { get; set; }

            [SDKRequired]
            [SDKStringLength(120)]
            public required string AnyOtherField { get; set; }       
        }
        // END_ENTITY_FILE
        ```
        """
