import logging
import os
import chardet
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from feature_analyzer.common.step_execution_interface import StepExecutionInterface
from feature_analyzer.models.application_files_model import ApplicationFileModel


class MapFilesStepService(StepExecutionInterface):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def execute(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        try:

            data_wrapper.database_tables_content = self.__read_content_from_file(
                data_wrapper.database_tables_file_path
            )

            data_wrapper.procedure_files_mapping = (
                self.__create_procedures_files_mapping(data_wrapper.procedures_dir_path)
            )

            data_wrapper.output_app_files_mapping = self.__create_application_files_mapping(
                application_files_dir_path=data_wrapper.application_files_dir_path,
                application_files_names_to_consider=data_wrapper.application_files_names_to_consider,
            )

        except Exception as error:
            self.logger.error(f"❌ Error on preparing the tables content: {error}.")

        return data_wrapper

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
