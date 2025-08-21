from prompter.base import ConfigAuthentication
from langchain_openai import ChatOpenAI
from generativeai.base_prompter import BasePrompter


class PrompterOpenAI(BasePrompter):
    def __init__(
        self, config_auth: ConfigAuthentication, model: str, use_agent: bool = False
    ) -> None:
        """Initialize a new Prompter instance."""
        self.model_instance = ChatOpenAI(
            model=model,
            api_key=config_auth.openai_api_key,
            base_url=config_auth.openai_base_url,
            default_headers=config_auth.openai_headers,
            temperature=0.0,
        )

        super().__init__(config_auth=config_auth, use_agent=use_agent)
