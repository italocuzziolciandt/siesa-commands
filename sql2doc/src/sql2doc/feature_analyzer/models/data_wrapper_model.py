import os
import chardet
import markdown
from datetime import datetime
from weasyprint import HTML
from .procedure_model import ProcedureModel
from .procedure_analysis_result_model import (
    ProcedureAnalysisResultModel,
)
from .database_table_model import DatabaseTableModel
from .application_files_model import ApplicationFileModel
from weasyprint.text.fonts import FontConfiguration


class DataWrapperModel:
    ## Inputs
    database_tables_content: str = None
    procedure_files_mapping: dict[str, str] = ()
    output_file_path: str = None
    procedure_entry_point_name: str = None
    use_tables_in_procedure_analysis: bool = False
    application_files_dir_path: str
    application_files_names_to_consider: list[str]

    # Outputs
    output_tables_mapping: list[DatabaseTableModel] = []
    output_procedures_mapping: list[ProcedureModel] = []
    output_app_files_mapping: list[ApplicationFileModel] = []
    output_procedure_analysis_result: list[ProcedureAnalysisResultModel] = []
    output_database_model_full_content: str = ""
    output_use_cases_doc_full_content: str = ""
    output_entities_code_full_content: str = ""
    output_business_code_full_content: str = ""
    output_sequence_diagram_full_content: str = ""
    output_flow_diagram_full_content: str = ""

    def __init__(
        self,
        database_tables_file_path: str,
        procedures_dir_path: str,
        procedure_entry_point_file_name: str,
        use_tables_in_procedure_analysis: bool,
        application_files_dir_path: str,
        application_files_names_to_consider: list[str],
        output_file_path: str,
    ):
        self.database_tables_content = self.__read_content_from_file(
            database_tables_file_path
        )
        self.procedure_files_mapping = self.__create_procedures_files_mapping(
            procedures_dir_path
        )
        self.procedure_entry_point_name = procedure_entry_point_file_name
        self.use_tables_in_procedure_analysis = use_tables_in_procedure_analysis

        self.output_app_files_mapping = self.__create_application_files_mapping(
            application_files_dir_path=application_files_dir_path,
            application_files_names_to_consider=application_files_names_to_consider,
        )

        self.output_file_path = output_file_path

    def write_output(self) -> None:
        """
        Writes each section of the output to separate Markdown files
        within a timestamped directory.  Also generates a PDF
        from the use cases documentation.
        """

        timestamped_dir = self.__create_timestamped_directory()

        self.__write_output_section(
            self.output_database_model_full_content,
            os.path.join(timestamped_dir, "database_model.md"),
        )
        self.__write_output_section(
            self.output_use_cases_doc_full_content,
            os.path.join(timestamped_dir, "use_cases_documentation.md"),
        )
        self.__write_output_section(
            self.output_entities_code_full_content,
            os.path.join(timestamped_dir, "entities_code.md"),
        )
        self.__write_output_section(
            self.output_business_code_full_content,
            os.path.join(timestamped_dir, "business_code.md"),
        )

        self.__write_output_section(
            self.output_sequence_diagram_full_content,
            os.path.join(timestamped_dir, "sequence_diagram.md"),
        )
        self.__write_output_section(
            self.output_flow_diagram_full_content,
            os.path.join(timestamped_dir, "flow_diagram.md"),
        )

        pdf_path = os.path.join(timestamped_dir, "use_cases_documentation.pdf")
        self.__generate_pdf_from_markdown(
            self.output_use_cases_doc_full_content, pdf_path
        )

    def __generate_pdf_from_markdown(self, markdown_content: str, output_path: str):
        """
        Generates a PDF file from Markdown content, ensuring proper handling of line breaks and other formatting.

        Args:
            markdown_content (str): The Markdown content to convert.
            output_path (str): The path to save the generated PDF file.
        """
        try:
            # Convert Markdown to HTML with line break support
            html = markdown.markdown(markdown_content, extensions=["nl2br"])

            # Create a WeasyPrint FontConfiguration object
            font_config = FontConfiguration()

            # Write the HTML content to a PDF file
            HTML(string=html).write_pdf(output_path, font_config=font_config)

            print(f"Successfully generated Use Case PDF: {output_path}")

        except Exception as e:
            print(f"Error generating PDF: {e}")

    def __create_timestamped_directory(self) -> str:
        """
        Creates a timestamped directory within the main output folder.

        Returns:
            str: The path to the newly created directory.
        """
        main_output_folder = os.path.dirname(self.output_file_path)
        now = datetime.now()
        timestamp = now.strftime("%Y_%m_%d_%H_%M")
        dir_name = f"output"
        output_dir = os.path.join(main_output_folder, dir_name)

        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def __write_output_section(self, content: str, file_path: str) -> None:
        """
        Writes the given content to the specified file.

        Args:
            content (str): The content to write.
            file_path (str): The full path to the output file.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Successfully wrote to {file_path}")
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")

    def __create_procedures_files_mapping(self, procedures_path: str) -> dict[str, str]:
        """
        Creates a mapping of file paths to content for all procedure files in a directory.

        Args:
            procedures_path (str): The path to the directory containing the procedure files.

        Returns:
            Dict[str, str]: A dictionary where keys are file paths and values are the file content.
        """

        all_files_path = self.__get_all_files_from_path(procedures_path)

        if not all_files_path:
            return "No files found in the specified path."

        files_mapping = dict[str, str]()

        for file_path in all_files_path:
            content = self.__read_content_from_file(file_path)
            if not content:
                continue

            files_mapping[file_path] = content

        return files_mapping

    def __create_application_files_mapping(
        self,
        application_files_dir_path: str,
        application_files_names_to_consider: list[str],
    ) -> list[ApplicationFileModel]:
        """
        Creates a mapping of application files to their content.

        Args:
            application_file_dir (str): The directory containing the application files.
            application_files_to_consider (list[str]): The list of application file names to consider.

        Returns:
            list[ApplicationFileModel]: A list of ApplicationFileModel instances.
        """
        application_files_mapping = []
        all_files_path = self.__get_all_files_from_path(
            application_files_dir_path, recursive=True
        )

        for file_path in all_files_path:
            file_name = os.path.basename(file_path)
            if file_name in application_files_names_to_consider:
                content = self.__read_content_from_file(file_path)
                if content:
                    application_files_mapping.append(
                        ApplicationFileModel(
                            file_name=file_name,
                            file_content=content,
                            method_names=self.__get_method_list(file_name),
                        )
                    )

        return application_files_mapping

    def __get_method_list(self, file_name: str) -> list[str]:
        switcher = {
            "ControladorNomLiqProTiemposBasicos.java": ["handle"],
            "nomNomLiqProTiemposBasicos.js": None,
            "AdministradoresNomina3Mngr.java": [
                "procesarNomLiqProTiemposBasicos",
                "consultarNomLiqProLiquidaciones",
                "consultaTotalLiq",
            ],
            "ConsultantesNomina3_2Mngr.java": ["consultarW0050ParametrosNomina"],
        }

        return switcher.get(file_name, [])

    def __read_content_from_file(self, content_path: str) -> str:
        """
        Reads content from a file by detecting its encoding.

        :param content_path: The path to the file containing the content.
        :return: The content as a string.
        """
        try:
            # Read the file in binary mode to detect the encoding
            with open(content_path, "rb") as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result.get("encoding", "utf-8")

            # Now decode using the detected encoding
            return raw_data.decode(encoding, errors="replace")
        except FileNotFoundError:
            print(f"Error: The file {content_path} does not exist.")
            return ""
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
            return ""

    def __get_all_files_from_path(
        self, content_path: str, recursive: bool = False
    ) -> list[str]:
        """
        Retrieves a list of all files within a given directory, optionally searching recursively.

        Args:
            content_path (str): The path to the directory.
            recursive (bool): Whether to search for files recursively in subdirectories. Defaults to False.

        Returns:
            list[str]: A list of absolute file paths within the directory. Returns an empty list
                    if the path does not exist.
        """

        if not os.path.exists(content_path):
            print(f"Error: The path {content_path} does not exist.")
            return []

        file_list = []

        if recursive:
            for root, _, files in os.walk(content_path):
                for file in files:
                    file_list.append(os.path.join(root, file))
        else:
            file_list = [
                os.path.join(content_path, f)
                for f in os.listdir(content_path)
                if os.path.isfile(os.path.join(content_path, f))
            ]

        return file_list
