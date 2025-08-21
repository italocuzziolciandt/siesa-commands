from feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


class EntitiesFromTableContentPrompt(AnalyzerPrompt):
    def __init__(
        self,
        table_name: str,
        table_content: str,
        database_model_diagram: str,
        table_new_name_convention: str = None,
    ) -> None:
        self.table_name = table_name
        self.table_content = table_content
        self.database_model_diagram = database_model_diagram
        self.table_new_name_convention = table_new_name_convention

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
        We are modernizing an legacy application from Java to .NET C#. For the new application, we need to generate the Entities. The Entities are responsible for representing the database tables in the new application using Entity Framework Core.

        This is the database table that needs to map as an Entity:
        ```sql
        {self.table_content}
        ```

        Provide the Entity implementation, that represents and modernizes the tables.

        { 
            f"The new name of the entity should be (follow the code guidelines): {self.table_new_name_convention}" 
            if self.table_new_name_convention is not None else "" 
        }

        Strictly follow the example below:
        {self.__get_entity_example()}

        Coding Guidelines:
        - The entity should inherit from the BaseMaster base class.
        - The names of the entities are defined with an initial letter that describes their role and a 5-digit code where the first two define the service code and the remaining ones a unique code (example: E30010_Client).
        - Properties that are already defined in the base classes should not be redefined (ignore them), specially the audit properties (CreationDate, LastUpdateDate, CreationUser, LastUpdateUser, etc).
        - Add the `required` modifier to string properties that are not nullable.
        - Use the annotations:
        -- SDKRequired: For database required fields.
        -- SDKStringLength: To defined the max length of varchar columns.
        -- ForeignKey: To define foreign key relationships when applicable.

        Here you have the base classes definitions:
        {self.__get_base_classes_definitions()}

        The relationship between the entities should be clearly defined, including any foreign key relationships defined in the database model diagram:
        ```mermaid
        {self.database_model_diagram}
        ```

        Provide a **complete entity class implementation**, without summarizing or truncating the response. If the response exceeds the max output limit, continue generating until all services are fully covered.

        After generating the entity, use the tool `write_class_content_to_file` to write the class content to a file.

        Important:
        - To provide the relationship between the entities, only include the relevant foreign key for this specific entity.
        - Don't make assumptions, provide the full entity implementation of the class.
        - Don't add any additional comments or explanations, just provide the code implementation.
        """

    def get_messages(self) -> list[BaseMessage]:
        return [
            SystemMessage(content=self.get_system_message()),
            HumanMessage(content=self.get_user_message()),
        ]

    def __get_base_classes_definitions(self) -> str:
        return """
        ```csharp
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
        using System.ComponentModel.DataAnnotations;
        using Siesa.SDK.Entities;
        using Siesa.SDK.Shared.DataAnnotations;

        /// <summary>
        /// Represents a payroll movement (or transaction) within the system.
        /// Inherits from <see cref="BaseMaster{int, string}"/>, indicating it's a master data entity with an integer key and string identifier.
        /// </summary>
        public class E0602_MovtoNomina : BaseMaster<int, string>
        {
            [SDKIdentity]
            [Key]
            [SDKRequired]
            public int RowId { get; set; }

            [SDKRequired]
            public int IdCompany { get; set; }

            [SDKRequired]
            public int RowIdDoctoNomina { get; set; }

            [SDKStringLength(100)]
            public string Name { get; set; }
            
            [SDKRequired]
            [SDKStringLength(120)]
            public required string Description { get; set; }            

            [ForeignKey("RowidInternalUser")]
            public virtual E00220_User? InternalUser { get; set; }

            [SDKStringLength(255)]
            public string? Notes { get; set; }
        }
        ```
        """
