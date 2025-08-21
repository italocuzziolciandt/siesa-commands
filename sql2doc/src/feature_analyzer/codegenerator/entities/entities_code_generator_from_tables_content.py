from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from feature_analyzer.codegenerator.code_generator_service_interface import (
    CodeGeneratorServiceInterface,
)
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from generativeai.prompter_interface import PrompterInterface
from feature_analyzer.models.database_table_model import DatabaseTableModel
from feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from feature_analyzer.codegenerator.prompts.entities_from_table_content_prompt import (
    EntitiesFromTableContentPrompt,
)
from feature_analyzer.feature_toggle import feature_toggle_instance
from generativeai.prompter_factory import PrompterFactory
from feature_analyzer.app_config import app_config_instance

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class EntitiesCodeGeneratorFromTablesContent(CodeGeneratorServiceInterface):
    def __init__(self):
        self.prompter = PrompterFactory.create_prompter(
            config_auth=app_config_instance.get_config_auth(),
            model=app_config_instance.database_diagrams_llm_model,
        )
        self.logger = logging.getLogger(__name__)
        self.max_workers = 20

    def generate(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        try:
            if (
                not feature_toggle_instance.is_backend_entities_code_generation_enabled()
            ):
                self.logger.info(
                    "Entities code generation is disabled. Skipping generation."
                )
                return data_wrapper

            self._process_tables_content_in_parallel(data_wrapper.output_tables_mapping)

            entities_full_content = "\n".join(
                table.entity_code_llm_result
                for table in data_wrapper.output_tables_mapping
            )

            data_wrapper.output_entities_code_full_content = entities_full_content
        except Exception as error:
            self.logger.error(f"Error on generating the entities classes: {error}.")

        return data_wrapper

    def _process_tables_content_in_parallel(
        self, tables_mapping: list[DatabaseTableModel]
    ) -> None:
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._process_single_table, table): table
                for table in tables_mapping
            }

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(
                        f"Error generating entities code from tables content: {e}"
                    )

    def _process_single_table(self, table: DatabaseTableModel) -> None:
        self.logger.info(f"Generating entity code for table: {table.name}")

        prompt: AnalyzerPrompt = EntitiesFromTableContentPrompt(
            table_name=table.name,
            table_content=table.content,
        )

        entity_code_result = self.prompter.get_content_from_invoke_llm_with_messages(
            prompt.get_messages()
        )

        table.entity_code_llm_result = entity_code_result

        self.logger.info(f"Entity code generated for table: {table.name}")
