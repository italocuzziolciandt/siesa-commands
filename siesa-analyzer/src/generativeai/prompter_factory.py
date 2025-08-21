from generativeai.prompter_interface import PrompterInterface
from prompter.base import ConfigAuthentication
from generativeai.prompter_gemini import PrompterGemini
from generativeai.prompter_openai import PrompterOpenAI
from enum import Enum


class LLMModelNames(Enum):
    OPENAI_MODEL: str = "gpt-4.1"
    OPENAI_GTP5_MODEL: str = "gpt-5"
    OPENAI_GTP5_MINI_MODEL: str = "gpt-5-mini"
    GEMINI_FLASH_MODEL: str = "gemini-2.0-flash"
    GEMINI_PRO_MODEL: str = "gemini-2.5-pro"
    TIKTOKEN_MODEL: str = "gpt-4o"


class PrompterFactory:
    @staticmethod
    def create_prompter(
        config_auth: ConfigAuthentication, model: str, use_agent: bool = False
    ) -> PrompterInterface:
        """
        Factory method to create a Prompter instance based on the configuration.

        Args:
            config_auth (ConfigAuth): The authentication configuration for the language model.
            model (str): The name of the language model to use.
            use_agent (bool): Whether to use an agent-based prompt or not.

        Returns:
            Prompter: An instance of the Prompter class.
        """
        if model.startswith("gemini"):
            return PrompterGemini(
                config_auth=config_auth, model=model, use_agent=use_agent
            )
        elif model.startswith("gpt") or model.startswith("o3"):
            return PrompterOpenAI(
                config_auth=config_auth, model=model, use_agent=use_agent
            )
        else:
            raise ValueError(
                f"Unsupported model type: {model}. Supported models are Gemini and OpenAI."
            )
