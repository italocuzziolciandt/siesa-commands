from retry import retry
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AnyMessage
from langchain.chat_models.base import BaseChatModel
from pydantic import BaseModel
from generativeai.prompter_interface import PrompterInterface
from langgraph.prebuilt import create_react_agent
from generativeai.prompter_agent_tools import (
    write_partial_result,
    log_step,
    write_class_content_to_file,
)
from typing import Any, Callable, Union, Dict
from collections.abc import Sequence
from langchain_core.tools import BaseTool
from prompter.base import ConfigAuthentication


class BasePrompter(PrompterInterface):
    model_instance: BaseChatModel
    use_agent: bool
    config_auth: ConfigAuthentication

    def __init__(self, config_auth: ConfigAuthentication, use_agent: bool) -> None:
        self.config_auth = config_auth
        self.use_agent = use_agent

        if self.use_agent:
            self.agent = create_react_agent(
                model=self.model_instance,
                tools=[write_partial_result, log_step, write_class_content_to_file],
                debug=False,
            )

    def get_config_auth(self) -> ConfigAuthentication:
        """Returns the configuration authentication object."""
        return self.config_auth

    @retry(tries=1, delay=10)
    def invoke_llm(
        self, system_message: str, prompt: str, recursion_limit: int = 100
    ) -> AnyMessage:
        """Invokes the language model with a system message and a prompt."""

        if self.use_agent:
            response = self.agent.invoke(
                {
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt},
                    ]
                },
                {"recursion_limit": recursion_limit},
            )
            return response["messages"][-1].content

        response = self.model_instance.invoke(
            [
                SystemMessage(content=system_message),
                HumanMessage(content=prompt),
            ]
        )

        return response

    @retry(tries=1, delay=10)
    def invoke_llm_with_messages(
        self, messages: list[BaseMessage], recursion_limit: int = 200
    ) -> AnyMessage:
        """Invokes the language model with a list of messages."""
        if self.use_agent:
            response = self.agent.invoke(
                {"messages": messages},
                {"recursion_limit": recursion_limit},
            )
            # Return the last message in the response
            return response["messages"][-1].content

        response = self.model_instance.invoke(messages)
        return response

    def get_content_from_invoke_llm_with_messages(
        self, messages: list[BaseMessage], recursion_limit: int = 200
    ) -> str:
        """Invokes the language model with a list of messages."""
        result_message = self.invoke_llm_with_messages(messages, recursion_limit)
        if self.use_agent:
            return result_message

        return result_message.content

    @retry(tries=1, delay=10)
    def get_structured_output_from_llm(
        self, messages: list[BaseMessage], recursion_limit: int = 200
    ) -> BaseModel:
        """Retrieves a structured output from the language model based on a list of messages."""
        if self.use_agent:
            response = self.agent.invoke(
                {"messages": messages},
                {"recursion_limit": recursion_limit},
            )
            return response["structured_response"]

        return self.model_instance.invoke(messages)

    def bind_model(self, structured_output_class: BaseModel) -> None:
        """Binds a new model to the Prompter instance."""
        if self.use_agent:
            self.agent = create_react_agent(
                model=self.model_instance,
                tools=[write_partial_result, log_step, write_class_content_to_file],
                debug=False,
                response_format=structured_output_class,
            )
            return

        self.model_instance = self.model_instance.with_structured_output(
            structured_output_class
        )

    def bind_tools(
        self, tools: Sequence[Union[Dict[str, Any], type, Callable, BaseTool]]
    ) -> None:
        self.model_instance = self.model_instance.bind_tools(tools)
