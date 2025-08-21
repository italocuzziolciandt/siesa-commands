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
    tables_new_name_convention: dict[str, str]

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

        self.tables_new_name_convention = self.__get_table_names_mapping()

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

    def __get_table_names_mapping(self) -> dict:
        return {
            "t021_mm_tipos_documentos": "e20120_document_type",
            "t016_mm_bancos": "e20130_bank",
            "t285_co_centro_op": "e20160_operation_center",
            "t011_mm_paises": "e20200_country",
            "t012_mm_deptos": "e20201_state",
            "t013_mm_ciudades": "e20202_city",
            "t284_co_ccosto": "e20233_cost_center_auxiliary",
            "t279_co_grupos_ccostos": "e20235_cost_center_group",
            "t107_mc_proyectos": "e20253_project_auxiliary",
            "t024_mm_periodos": "e20271_fiscal_period",
            "t053_mm_fechas": "e20272_fiscal_date",
            "t281_co_unidades_negocio": "e20280_business_unit",
            "w0763_gh01_cargos": "e20310_position",
            "t203_mm_tipo_ident": "e20400_identification_type",
            "t200_mm_terceros": "e20410_third_party",
            "w0501_conceptos": "e77501_conceptos",
            "w0502_agrupacion_conceptos": "e77502_agrupacion_conceptos",
            "w0503_detalle_agrupac_cptos": "e77503_detalle_agrupac_cptos",
            "w0504_tipos_nomina": "e77504_tipos_nomina",
            "w0510_grupos_empleados": "e77510_grupos_empleados",
            "w0511_detalle_grupo_empleados": "e77511_detalle_grupo_empleados",
            "w0514_cod_nal_entidades": "e77514_cod_nal_entidades",
            "w0515_entidades_eps": "e77515_entidades_eps",
            "w0516_entidades_afp": "e77516_entidades_afp",
            "w0517_entidades_arp": "e77517_entidades_arp",
            "w0518_entidades_cajas": "e77518_entidades_cajas",
            "w0519_entidades_sena": "e77519_entidades_sena",
            "w0520_entidades_icbf": "e77520_entidades_icbf",
            "w0521_entidades_fondos": "e77521_entidades_fondos",
            "w0522_entidades_afc": "e77522_entidades_afc",
            "w0530_centros_de_trabajo": "e77530_centros_de_trabajo",
            "w0535_tipos_cotizante": "e77535_tipos_cotizante",
            "w0540_empleados": "e77540_empleados",
            "w0051_parametros_nomina_ano": "e77541_parametros_nomina_anio",
            "w0050_parametros_nomina": "e77542_parametros_nomina",
            "w0550_contratos": "e77550_contratos",
            "w0555_motivos_retiro": "e77555_motivos_retiro",
            "w0557_contratos_distr_salario": "e77557_contratos_distr_salario",
            "w0558_contratos_sueldos_log": "e77558_contratos_sueldos_log",
            "w0580_periodos_nomina": "e77580_periodos_nomina",
            "w0581_periodos_nomina_detalle": "e77581_periodos_nomina_detalle",
            "w0600_docto_nomina": "e77600_docto_nomina",
            "w0601_docto_nomina_emp": "e77601_docto_nomina_emp",
            "w0602_movto_nomina": "e77602_movto_nomina",
            "w0610_tiempo_no_laborado": "e77610_tiempo_no_laborado",
            "w0611_tiempo_no_labor_detalle": "e77611_tiempo_no_labor_detalle",
            "w0618_ausentismos": "e77618_ausentismos",
            "w0643_autoliquid_sucursales": "e77643_autoliquid_sucursales",
        }
