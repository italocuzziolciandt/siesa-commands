import logging
import sys
from prompter.base import ConfigAuthentication
from generativeai.prompter_factory import LLMModelNames
from phoenix.otel import register
from openinference.instrumentation import OITracer
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry.sdk.trace import TracerProvider


class AppConfig:
    _instance = None
    _config_auth: ConfigAuthentication
    _phoenix_project_name: str = "siesa-modernization-feature-analyzer"
    _phoenix_endpoint_url: str = "http://localhost:6006/v1/traces"

    tracer: OITracer = None
    ## Models to use in the analysis
    prepare_tables_tiktoken_model: str = LLMModelNames.TIKTOKEN_MODEL.value
    prepare_procedures_tiktoken_model: str = LLMModelNames.TIKTOKEN_MODEL.value
    database_diagrams_llm_model: str = LLMModelNames.OPENAI_MODEL.value
    use_case_analysis_llm_model: str = LLMModelNames.GEMINI_FLASH_MODEL.value
    backend_entities_llm_model: str = LLMModelNames.OPENAI_MODEL.value
    backend_business_llm_model: str = LLMModelNames.GEMINI_FLASH_MODEL.value

    # General Configurations
    max_procedure_analysis_dependency_depth: int = -1

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls.tracer = cls._instance.__register_trace()

        return cls._instance

    def set_config_auth(self, config_auth: ConfigAuthentication) -> None:
        self._config_auth = config_auth

    def get_config_auth(self) -> ConfigAuthentication:
        return self._config_auth

    def configure_logging(self) -> None:
        logging.basicConfig(
            level=logging.INFO, 
            format="%(asctime)s - %(levelname)s - %(message)s",
            stream=sys.stderr,
        )

    def __register_trace(self) -> OITracer:
        tracer_provider: TracerProvider = register(
            project_name=self._phoenix_project_name,
            endpoint=self._phoenix_endpoint_url,
            auto_instrument=False,
            set_global_tracer_provider=False,
        )

        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

        return tracer_provider.get_tracer(__name__)


# Singleton instance
app_config_instance = AppConfig()
