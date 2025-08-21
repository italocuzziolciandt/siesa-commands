from prompter.base import ConfigAuthentication
from generativeai.base_prompter import BasePrompter
from generativeai.flow_gemini_chat_model import FlowGeminiChatModel


class PrompterGemini(BasePrompter):
    def __init__(
        self, config_auth: ConfigAuthentication, model: str, use_agent: bool = False
    ) -> None:
        """Initialize a new Prompter instance."""
        self.flowHeaders = config_auth.openai_headers

        self.model_instance = FlowGeminiChatModel(
            model=model,
            api_token=config_auth.openai_api_key,
            default_headers=self.flowHeaders,
            temperature=0.0,
            flow_agent=self.flowHeaders["FlowAgent"],
            flow_tenant="gucentauru",
        )

        super().__init__(config_auth=config_auth, use_agent=use_agent)
