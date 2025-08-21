from abc import ABC, abstractmethod
from langchain_core.messages import BaseMessage, AnyMessage
from langchain.chat_models.base import BaseChatModel
from pydantic import BaseModel
from typing import Any, Callable, Union, Dict
from collections.abc import Sequence
from langchain_core.tools import BaseTool
from prompter.base import ConfigAuthentication


class PrompterInterface(ABC):
    model: BaseChatModel
    config_auth: ConfigAuthentication
    use_agent: bool

    @abstractmethod
    def get_config_auth(self) -> ConfigAuthentication:
        """Returns the configuration authentication object."""
        pass

    @abstractmethod
    def invoke_llm(
        self, system_message: str, prompt: str, recursion_limit: int
    ) -> AnyMessage:
        """Invokes the language model with a system message and a prompt."""
        pass

    @abstractmethod
    def invoke_llm_with_messages(
        self, messages: list[BaseMessage], recursion_limit: int
    ) -> AnyMessage:
        """Invokes the language model with a list of messages."""
        pass

    @abstractmethod
    def get_content_from_invoke_llm_with_messages(
        self, messages: list[BaseMessage], recursion_limit: int
    ) -> str:
        """Invokes the language model with a list of messages."""
        pass

    @abstractmethod
    def get_structured_output_from_llm(
        self, messages: list[BaseMessage], recursion_limit: int
    ) -> BaseModel:
        """Retrieves a structured output from the language model based on a list of messages."""
        pass

    @abstractmethod
    def bind_model(self, structured_output_class: BaseModel) -> None:
        """Binds a new model to the Prompter instance."""
        pass

    @abstractmethod
    def bind_tools(
        self, tools: Sequence[Union[Dict[str, Any], type, Callable, BaseTool]]
    ) -> None:
        pass
