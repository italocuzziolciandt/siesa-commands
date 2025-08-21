from feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


class GenerateDbContextPrompt(AnalyzerPrompt):
    def __init__(
        self,
        entities_signatures: str,
        database_model_diagram: str
    ) -> None:
        self.entities_signatures = entities_signatures
        self.database_model_diagram = database_model_diagram

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
            We need to generate the Entity Framework DBContext class based on a template and a list of entity definitions. 
            The Entities are responsible for representing the database tables in the new application using Entity Framework Core.

            This is the template that you need to use to implement the DbContext:
            ```csharp
            {self.__get_dbcontext_template_example()}
            ```

            Here you have the entities signatures:
            ```csharp
            {self.entities_signatures}
            ```

            Provide me the DbContext implementation.

            Here you have the base class definition to use as reference:
            {self.__get_base_classes_definitions()}

            Provide a **complete DbContext class implementation**, without summarizing or truncating the response. If the response exceeds the max output limit, continue generating until all entities are fully covered.

            After generating the DbContext, use the tool `write_class_content_to_file` to write the class content to a file.

            Important:
            - Don't make assumptions, provide the full DbContext implementation of the class.
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
        public class SDKContext : DbContext
        {
            // Fields
            public static readonly string TemporalTablePrefix;

            // Constructor
            public SDKContext(DbContextOptions options);

            // Methods
            public void SetProvider(IServiceProvider serviceProvider);
            public void ResetConcurrencyValues(object entity, object UpdatedEntity);
            public EnumDBType GetEnumDBType();
            public int SaveSystemChanges();
            public override Task<int> SaveChangesAsync(CancellationToken cancellationToken = default(CancellationToken));
            public override int SaveChanges();
            internal int InternalSaveChanges(bool ValidateUser = true);
            public DbSet<TEntity> AllSet<TEntity>() where TEntity : class;
            public override DbSet<TEntity> Set<TEntity>() where TEntity : class;
            public DbSet<TEntity> Set<TEntity>(bool ignoreVisibility) where TEntity : class;
            protected override void ConfigureConventions(ModelConfigurationBuilder configurationBuilder);
            protected override void OnModelCreating(ModelBuilder modelBuilder);
            protected virtual void AddCustomDbFunctions(ModelBuilder modelBuilder, EnumDBType BdUsed, List<SDKColumnByDatabaseEngine> ColumnsByEngine);
            public void ExecuteStoreProcedure(string nameSp, List<SDKSQLParameter> parameters);
            public List<List<dynamic>> ExecuteStoreProcedure(string procedureName, ICollection<SDKSQLParameter> parameters, List<Type> outputTypes);
            public override void Dispose();
            internal static void UpdateEntityType(IEntityType entityType, string newTableName);
            internal static void UpdateTableMappings(IEntityType entityType, string newTableName);
            internal void MapTemporaryTable(string temporaryTableName, Type TemporalType, EnumDBType DbType, ref string TemporalQueryRef, ref string PrimaryKeyConstraintRef);
            internal string GetTableNameFromAnnotations(Type DestinationType);
            internal string GetTableName(Type DestinationTableType, string? CustomTableName);
            internal string GenerateCreateQuery(ref string TableName, IQueryable Query, EnumDBType DbType, out object[] Parameters);
            internal static void GenerateKeyConstraint(string TableName, string PropertyName, EnumDBType DbType, Type TemporalType, ref string TemporalQueryRef, ref string PrimaryKeyConstraintRef);
            public int InsertInTemporalTableFromQuery<TEntity>(IQueryable<TEntity> query, Type DestinationTable, string? TableName = null) where TEntity : class;
            internal void DropTableIfExists(string TableName);
            internal static string GetClassNameSintax(Type PropertyType);
            internal static string GetClassNameSintax(string NameOfPropertyType);
            internal static string GenerateCreateQuery(FrozenSet<string> Columns, EnumDBType DbType, ref string TableName);
            public void CreateTemporaryTable(Type DestinationTable, string? TableName = null);
            public void BeginTransaction();
            public void Commit();
            public void Rollback();
            public Task BeginTransactionAsync();
            public Task CommitAsync();
            public Task RollbackAsync();
            public void CreateSavepoint(string name);
            public Task CreateSavepointAsync(string name, CancellationToken cancellationToken = default(CancellationToken));
            public void RollbackToSavepoint(string name);
            public Task RollbackToSavepointAsync(string name, CancellationToken cancellationToken = default(CancellationToken));
            public void ReleaseSavepoint(string name);
            public Task ReleaseSavepointAsync(string name, CancellationToken cancellationToken = default(CancellationToken));
        }        
        ```
        """

    def __get_dbcontext_template_example(self) -> str:
        return """
        ```csharp
        using Microsoft.EntityFrameworkCore;
        using Siesa.SDK.Backend.Access;
        using System;
        using System.Collections.Generic;
        using System.Linq;
        using System.Text;
        using System.Threading.Tasks;
        using POCCIT.LiquidationService.Shared;

        namespace POCCIT.LiquidationService.Access.Context
        {
            public class LiquidationServiceContext : SDKContext
            {
                public LiquidationServiceContext(DbContextOptions options) : base(options)
                {
                    // DbSet IMPLEMENTATION GOES HERE

                    protected override void OnModelCreating(ModelBuilder modelBuilder)
                    {
                        base.OnModelCreating(modelBuilder);
                        // Custom model configuration goes here
                    }                    
                }
            }
        }
        ```
        """
