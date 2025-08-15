import logging
from prompter.base import ConfigAuthentication
from .models.data_wrapper_model import DataWrapperModel
from .preparation.prepare_tables_content_service import (
    PrepareTablesContentService,
)
from .preparation.prepare_procedures_content_service import (
    PrepareProceduresContentService,
)
from .documentation.analyzer_service_interface import (
    AnalyzeServiceInterface,
)
from .codegenerator.code_generator_service_interface import (
    CodeGeneratorServiceInterface,
)
from .codegenerator.code_generator_service import (
    CodeGeneratorService,
)
from sql2doc.common.loading_animation import LoadingAnimation
from .documentation.documentation_generator_service import (
    DocumentationGeneratorService,
)
from .app_config import app_config_instance

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AnalyzerService:
    prepare_tables_content_service: PrepareTablesContentService
    prepare_procedures_content_service: PrepareProceduresContentService
    documentation_generator_service: AnalyzeServiceInterface
    code_generator_service: CodeGeneratorServiceInterface
    output_file_path: str

    def __init__(self, config_auth: ConfigAuthentication):
        """Initializes the AnalyzerService with the given configuration."""
        app_config_instance.set_config_auth(config_auth)
        self.logger = logging.getLogger(__name__)

        self.prepare_tables_content_service = PrepareTablesContentService()
        self.prepare_procedures_content_service = PrepareProceduresContentService()
        self.documentation_generator_service = DocumentationGeneratorService()
        self.code_generator_service = CodeGeneratorService()

    def analyze_feature(
        self,
        database_tables_file_path: str,
        procedure_entry_point_file_name: str,
        procedures_dir_path: str,
        application_files_dir_path: str,
        application_files_names_to_consider: list[str],
        output_file_path: str,
    ) -> None:
        """Analyzes a database feature given the specified file paths and generates code."""
        self.logger.info(f"Starting analysis for feature...")

        data_wrapper = DataWrapperModel(
            database_tables_file_path=database_tables_file_path,
            procedures_dir_path=procedures_dir_path,
            procedure_entry_point_file_name=procedure_entry_point_file_name,
            use_tables_in_procedure_analysis=False,
            application_files_dir_path=application_files_dir_path,
            application_files_names_to_consider=application_files_names_to_consider,
            output_file_path=output_file_path,
        )

        self.logger.info(f"[Preparation] Preparing input data for analysis...")
        with LoadingAnimation(message="Preparation] Preparing tables..."):
            self.prepare_tables_content_service.prepare_tables_content(data_wrapper)

        with LoadingAnimation(message="Preparation] Preparing procedures..."):
            self.prepare_procedures_content_service.prepare_procedures_content(
                data_wrapper
            )
        self.logger.info(f"Preparation] Preparation completed.")

        self.logger.info(f"[Analysis Phase] Generating documentation...")
        with LoadingAnimation(message="[Analysis Phase] Generating documentation..."):
            self.documentation_generator_service.analyze(data_wrapper)
        self.logger.info(f"[Analysis Phase] Documentation generation completed.")

        self.logger.info(f"[Code Generation] Generating code...")
        with LoadingAnimation(message="[Code Generation] Generating code..."):
            self.code_generator_service.generate(data_wrapper)
        self.logger.info(f"[Code Generation] Code generation completed.")

        self.logger.info(f"Writing output to file: {output_file_path}")
        with LoadingAnimation(message="Writing output..."):
            data_wrapper.write_output()

        self.logger.info(
            f"Analysis and code generation completed successfully. Output written to {output_file_path}."
        )
