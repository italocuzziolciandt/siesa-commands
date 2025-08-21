import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from feature_analyzer.models.database_table_model import DatabaseTableModel
from feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from feature_analyzer.codegenerator.entities.prompts.entities_from_table_content_prompt import (
    EntitiesFromTableContentPrompt,
)
from common.feature_toggle import feature_toggle_instance
from generativeai.prompter_factory import PrompterFactory
from common.app_config import app_config_instance
from opentelemetry.trace import Status, StatusCode
from feature_analyzer.models.llm_entity_class_result_model import (
    LLMEntityClassResultModel,
)
from feature_analyzer.common.step_execution_interface import StepExecutionInterface


class EntitiesCodeGenerationStepService(StepExecutionInterface):
    def __init__(self):
        self.prompter = PrompterFactory.create_prompter(
            config_auth=app_config_instance.get_config_auth(),
            model=app_config_instance.backend_entities_llm_model,
            use_agent=True,
        )
        self.logger = logging.getLogger(__name__)
        self.max_workers = 10

        self.prompter.bind_model(LLMEntityClassResultModel)

    def execute(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        try:
            if not feature_toggle_instance.is_backend_entities_code_enabled():
                self.logger.info(
                    "Entities code generation is disabled. Skipping generation."
                )
                return data_wrapper

            result_list = self._process_tables_content_in_parallel(
                data_wrapper.output_tables_mapping
            )
            data_wrapper.output_entities_analysis_result = result_list

            entities_full_content = "\n".join(
                entity_result.content for entity_result in result_list
            )

            data_wrapper.output_entities_code_full_content = entities_full_content
        except Exception as error:
            self.logger.error(f"Error on generating the entities classes: {error}.")

        return data_wrapper

    def _process_tables_content_in_parallel(
        self, tables_mapping: list[DatabaseTableModel]
    ) -> list[LLMEntityClassResultModel]:
        result_list: list[LLMEntityClassResultModel] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._process_single_table, table): table
                for table in tables_mapping
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        result_list.append(result)
                except Exception as e:
                    self.logger.error(
                        f"Error generating entities code from tables content: {e}"
                    )

        return result_list

    def _process_single_table(
        self, table: DatabaseTableModel
    ) -> LLMEntityClassResultModel:
        with app_config_instance.tracer.start_as_current_span(
            "EntitiesCodeGeneration",
            openinference_span_kind="chain",
        ) as span:
            try:
                span.set_input(
                    value={
                        "table_name": table.name,
                        "table_content": table.content,
                    }
                )

                self.logger.info(f"Generating entity code for table: {table.name}")

                prompt: AnalyzerPrompt = EntitiesFromTableContentPrompt(
                    table_name=table.name,
                    table_content=table.content,
                )

                entity_code_result: LLMEntityClassResultModel = (
                    self.prompter.get_structured_output_from_llm(prompt.get_messages())
                )

                self.logger.info(f"Entity code generated for table: {table.name}")

                span.set_output(entity_code_result.content)
                span.set_status(Status(StatusCode.OK))

                return entity_code_result
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return None
