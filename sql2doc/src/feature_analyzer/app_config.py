from prompter.base import ConfigAuthentication
from generativeai.prompter_factory import LLMModelNames


class AppConfig:
    _instance = None
    _config_auth: ConfigAuthentication

    ## Models to use in the analysis
    prepare_tables_tiktoken_model: str = LLMModelNames.TIKTOKEN_MODEL.value
    prepare_procedures_tiktoken_model: str = LLMModelNames.TIKTOKEN_MODEL.value
    database_diagrams_llm_model: str = LLMModelNames.OPENAI_MODEL.value
    use_case_analysis_llm_model: str = LLMModelNames.GEMINI_PRO_MODEL.value
    backend_entities_llm_model: str = LLMModelNames.OPENAI_MODEL.value
    backend_business_llm_model: str = LLMModelNames.GEMINI_PRO_MODEL.value

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)

        return cls._instance

    def set_config_auth(self, config_auth: ConfigAuthentication) -> None:
        self._config_auth = config_auth

    def get_config_auth(self) -> ConfigAuthentication:
        return self._config_auth


# Singleton instance
app_config_instance = AppConfig()
