import logging
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from common.feature_toggle import feature_toggle_instance
from generativeai.prompter_factory import PrompterFactory
from common.app_config import app_config_instance
from feature_analyzer.common.step_execution_interface import StepExecutionInterface
from feature_analyzer.models.llm_entity_class_result_model import (
    LLMEntityClassResultModel,
)
from feature_analyzer.codegenerator.entities.prompts.generate_db_context_prompt import (
    GenerateDbContextPrompt,
)
from opentelemetry.trace import Status, StatusCode


class DbContextCodeGenerationStepService(StepExecutionInterface):
    def __init__(self):
        self.prompter = PrompterFactory.create_prompter(
            config_auth=app_config_instance.get_config_auth(),
            model=app_config_instance.backend_entities_llm_model,
            use_agent=True,
        )
        self.logger = logging.getLogger(__name__)
        self.max_workers = 10

    def execute(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        try:
            if not feature_toggle_instance.is_backend_dbcontext_code_enabled():
                self.logger.info(
                    "DbContext code generation is disabled. Skipping generation."
                )
                return data_wrapper

            entities_signature = self.__get_entities_signatures(data_wrapper)
            dbcontext_full_content = self.__generate_dbcontext(
                entities_signature, data_wrapper.output_database_model_full_content
            )

            data_wrapper.output_dbcontext_code_full_content = dbcontext_full_content
        except Exception as error:
            self.logger.error(f"❌ Error on generating the DbContext class: {error}.")

        return data_wrapper

    def __generate_dbcontext(
        self, entities_signature: str, database_model_diagram: str
    ) -> str:
        with app_config_instance.tracer.start_as_current_span(
            "DbContextCodeGeneration",
            openinference_span_kind="chain",
        ) as span:
            try:
                span.set_input(
                    value={
                        "entities_signature": entities_signature,
                        "database_model_diagram": database_model_diagram,
                    }
                )

                prompt = GenerateDbContextPrompt(
                    entities_signatures=entities_signature,
                    database_model_diagram=database_model_diagram,
                )

                dbcontext_full_content = (
                    self.prompter.get_content_from_invoke_llm_with_messages(
                        prompt.get_messages()
                    )
                )

                span.set_output(dbcontext_full_content)
                span.set_status(Status(StatusCode.OK))

                return dbcontext_full_content
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return None

    def __get_entities_signatures(self, data_wrapper: DataWrapperModel) -> str:
        entities: list[LLMEntityClassResultModel] = (
            data_wrapper.output_entities_analysis_result
        )
        return "\n".join([entity.signature for entity in entities])
