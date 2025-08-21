import logging
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from feature_analyzer.prompts.analyzer_prompt_interface import AnalyzerPrompt
from common.feature_toggle import feature_toggle_instance
from generativeai.prompter_factory import PrompterFactory
from common.app_config import app_config_instance
from opentelemetry.trace import Status, StatusCode
from feature_analyzer.common.step_execution_interface import StepExecutionInterface
from feature_analyzer.codegenerator.entities.prompts.entities_from_diagram_content_prompt import (
    EntitiesFromDiagramContentPrompt,
)

class EntitiesCodeGenerationFromDiagramStepService(StepExecutionInterface):
    def __init__(self):
        self.prompter = PrompterFactory.create_prompter(
            config_auth=app_config_instance.get_config_auth(),
            model=app_config_instance.backend_entities_llm_model,
            use_agent=False,
        )
        self.logger = logging.getLogger(__name__)

    def execute(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        try:
            if not feature_toggle_instance.is_backend_entities_code_enabled():
                self.logger.info(
                    "Entities code generation is disabled. Skipping generation."
                )
                return data_wrapper

            if data_wrapper.output_database_model_full_content is None:
                raise ValueError("Database model diagram is missing.")

            entities_full_content = self._generate_entities(
                database_model_diagram=data_wrapper.output_database_model_full_content
            )

            data_wrapper.output_entities_code_full_content = entities_full_content
        except Exception as error:
            self.logger.error(f"❌ Error on generating the entities classes: {error}.")

        return data_wrapper

    def _generate_entities(self, database_model_diagram: str) -> str:
        with app_config_instance.tracer.start_as_current_span(
            "EntitiesCodeGeneration",
            openinference_span_kind="chain",
        ) as span:
            try:
                span.set_input(value=database_model_diagram)

                self.logger.info(f"Generating entities code from diagram...")

                prompt: AnalyzerPrompt = EntitiesFromDiagramContentPrompt(
                    database_model_diagram=database_model_diagram,
                )

                entity_code_result: str = (
                    self.prompter.get_content_from_invoke_llm_with_messages(
                        prompt.get_messages()
                    )
                )

                self.logger.info(f"✅ Entities code generated.")

                span.set_output(entity_code_result)
                span.set_status(Status(StatusCode.OK))

                return entity_code_result
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    # def split_entities(llm_output: str) -> dict[str, str]:
    #     print("Splitting entities from LLM output...")
        
    #     # Regex to find the filename and the code for each entity.
    #     # re.DOTALL is crucial for the `.` to match newline characters.
    #     pattern = re.compile(r"// START_ENTITY_FILE: (.*?\.cs)\s*(.*?)\s*// END_ENTITY_FILE", re.DOTALL)
        
    #     matches = pattern.finditer(llm_output)
        
    #     entities = {}
    #     for match in matches:
    #         filename = match.group(1).strip()
    #         csharp_code = match.group(2).strip()
    #         entities[filename] = csharp_code
            
    #     if not entities:
    #         print("Warning: No entities were found in the LLM output. Please check the delimiters.")
    #     else:
    #         print(f"Found {len(entities)} entities to be processed.")
            
    #     return entities