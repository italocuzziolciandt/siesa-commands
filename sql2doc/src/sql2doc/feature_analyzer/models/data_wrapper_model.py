import os
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from feature_analyzer.models.procedure_model import ProcedureModel
from feature_analyzer.models.procedure_analysis_result_model import (
    ProcedureAnalysisResultModel,
)
from feature_analyzer.models.database_table_model import DatabaseTableModel
from feature_analyzer.models.application_files_model import ApplicationFileModel
from feature_analyzer.models.llm_entity_class_result_model import (
    LLMEntityClassResultModel,
)
from feature_analyzer.preparation.files_handler_service import FilesHandlerService


class DataWrapperModel:
    """
    A data model that automatically writes output content to files
    in a timestamped directory as soon as the content is assigned.
    """

    # --- Input Properties ---
    database_tables_file_path: str
    procedures_dir_path: str
    procedure_entry_point_name: str
    application_files_dir_path: str
    application_files_names_to_consider: list[str]
    output_file_path: str
    output_timestamped_dir: str

    # -- Intermediate Properties
    database_tables_content: str
    procedure_files_mapping: dict[str, str]
    use_tables_in_procedure_analysis: bool

    # --- Internal State & Services ---
    files_handler: FilesHandlerService

    # --- Mappings for data that doesn't need immediate writing ---
    output_tables_mapping: list[DatabaseTableModel] = []
    output_procedures_mapping: list[ProcedureModel] = []
    output_app_files_mapping: list[ApplicationFileModel] = []
    output_procedure_analysis_result: list[ProcedureAnalysisResultModel] = []
    output_entities_analysis_result: list[LLMEntityClassResultModel] = []

    def __init__(
        self,
        database_tables_file_path: str,
        procedures_dir_path: str,
        procedure_entry_point_file_name: str,
        application_files_dir_path: str,
        application_files_names_to_consider: list[str],
        output_file_path: str,
    ):
        self.database_tables_file_path = database_tables_file_path
        self.procedures_dir_path = procedures_dir_path
        self.application_files_dir_path = application_files_dir_path
        self.application_files_names_to_consider = application_files_names_to_consider
        self.procedure_entry_point_name = procedure_entry_point_file_name
        self.output_file_path = output_file_path

        self.files_handler = FilesHandlerService()
        self.output_timestamped_dir = self.files_handler.create_timestamped_directory(
            self.output_file_path
        )

        self.database_tables_content = None
        self.procedure_files_mapping = {}
        self.use_tables_in_procedure_analysis = False

        # Initialize private backing fields for properties
        self._output_database_model_full_content: str = None
        self._output_use_cases_doc_full_content: str = None
        self._output_entities_code_full_content: str = None
        self._output_dbcontext_code_full_content: str = None
        self._output_business_code_full_content: str = None
        self._output_sequence_diagram_full_content: str = None
        self._output_flow_diagram_full_content: str = None

    def _write_output_section(self, content: str, filename: str):
        """
        Helper method to write a content section to a specific file
        within the timestamped output directory.
        """
        if content:
            full_path = os.path.join(self.output_timestamped_dir, filename)
            self.files_handler.write_output_section(content, full_path)
            print(f"Successfully wrote content to {full_path}")

    # --- Output Properties with Setters for Automatic File Writing ---
    @property
    def output_database_model_full_content(self) -> str:
        return self._output_database_model_full_content

    @output_database_model_full_content.setter
    def output_database_model_full_content(self, value: str):
        self._output_database_model_full_content = value
        self._write_output_section(value, "database_model.md")

    @property
    def output_use_cases_doc_full_content(self) -> str:
        return self._output_use_cases_doc_full_content

    @output_use_cases_doc_full_content.setter
    def output_use_cases_doc_full_content(self, value: str):
        self._output_use_cases_doc_full_content = value
        if value:
            # Write the Markdown file
            self._write_output_section(value, "use_cases_documentation.md")
            # Also generate the PDF
            pdf_path = os.path.join(
                self.output_timestamped_dir, "use_cases_documentation.pdf"
            )
            self.files_handler.generate_pdf_from_markdown(value, pdf_path)
            print(f"Successfully generated PDF at {pdf_path}")

    @property
    def output_entities_code_full_content(self) -> str:
        return self._output_entities_code_full_content

    @output_entities_code_full_content.setter
    def output_entities_code_full_content(self, value: str):
        self._output_entities_code_full_content = value
        self._write_output_section(value, "entities_code.md")

    @property
    def output_dbcontext_code_full_content(self) -> str:
        return self._output_dbcontext_code_full_content

    @output_dbcontext_code_full_content.setter
    def output_dbcontext_code_full_content(self, value: str):
        self._output_dbcontext_code_full_content = value
        self._write_output_section(value, "dbcontext_code.md")

    @property
    def output_business_code_full_content(self) -> str:
        return self._output_business_code_full_content

    @output_business_code_full_content.setter
    def output_business_code_full_content(self, value: str):
        self._output_business_code_full_content = value
        self._write_output_section(value, "business_code.md")

    @property
    def output_sequence_diagram_full_content(self) -> str:
        return self._output_sequence_diagram_full_content

    @output_sequence_diagram_full_content.setter
    def output_sequence_diagram_full_content(self, value: str):
        self._output_sequence_diagram_full_content = value
        self._write_output_section(value, "sequence_diagram.md")

    @property
    def output_flow_diagram_full_content(self) -> str:
        return self._output_flow_diagram_full_content

    @output_flow_diagram_full_content.setter
    def output_flow_diagram_full_content(self, value: str):
        self._output_flow_diagram_full_content = value
        self._write_output_section(value, "flow_diagram.md")
