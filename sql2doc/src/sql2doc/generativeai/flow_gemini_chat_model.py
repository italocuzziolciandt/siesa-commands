from __future__ import annotations
import json
import requests
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Mapping,
    Type,
    Union,
    AsyncIterator,
    Iterator,
    Callable,
)
from langchain_core.callbacks import (
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import BaseModel, Field, SecretStr
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Union,
)
from google.generativeai.types import Tool as GoogleTool
from google.generativeai.types.content_types import (
    ToolDict,
)
from langchain_core.callbacks.manager import (
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import AIMessage, BaseMessage, AIMessageChunk
from langchain_core.output_parsers.base import OutputParserLike
from langchain_core.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import (
    BaseModel,
    Field,
)
from langchain_google_genai._function_utils import (
    _ToolChoiceType,
    _ToolConfigDict,
    convert_to_genai_function_declarations,
    is_basemodel_subclass_safe,
    tool_to_dict,
)


class FlowGeminiChatModel(BaseChatModel):
    """Custom LLM wrapper for the specific Gemini API endpoint."""

    api_url: str = Field(
        "https://flow.ciandt.com/ai-orchestration-api/v1/google/generateContent",
        description="The API endpoint URL.",
    )
    api_token: Optional[SecretStr] = Field(None, description="The FLOW token.")
    flow_tenant: str = Field(None, description="FlowTenant.")
    flow_agent: str = Field(None, description="FlowAgent.")

    model_name: str = Field(
        default="gemini-2.5-pro", description="Allowed model identifier."
    )
    max_tokens: int = Field(default=65000, description="Maximum tokens to generate.")
    temperature: float = Field(default=0.7, description="Sampling temperature.")
    top_p: float = Field(default=0.9, description="Top P sampling.")
    top_k: int = Field(default=250, description="Top K sampling.")

    @property
    def _llm_type(self) -> str:
        return "flow-gemini"

    def bind_tools(
        self,
        tools: Sequence[Union[ToolDict, GoogleTool]],
        tool_config: Optional[Union[Dict, _ToolConfigDict]] = None,
        *,
        tool_choice: Optional[Union[_ToolChoiceType, bool]] = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, BaseMessage]:
        """Bind tool-like objects to this chat model.

        Assumes model is compatible with google-generativeAI tool-calling API.

        Args:
            tools: A list of tool definitions to bind to this chat model.
                Can be a pydantic model, callable, or BaseTool. Pydantic
                models, callables, and BaseTools will be automatically converted to
                their schema dictionary representation.
            **kwargs: Any additional parameters to pass to the
                :class:`~langchain.runnable.Runnable` constructor.
        """
        if tool_choice and tool_config:
            raise ValueError(
                "Must specify at most one of tool_choice and tool_config, received "
                f"both:\n\n{tool_choice=}\n\n{tool_config=}"
            )
        try:
            formatted_tools: list = [convert_to_openai_tool(tool) for tool in tools]  # type: ignore[arg-type]
        except Exception:
            formatted_tools = [
                tool_to_dict(convert_to_genai_function_declarations(tools))
            ]
        if tool_choice:
            kwargs["tool_choice"] = tool_choice
        elif tool_config:
            kwargs["tool_config"] = tool_config
        else:
            pass
        return self.bind(tools=formatted_tools, **kwargs)

    def _create_payload(
        self, messages: List[BaseMessage], stop_sequences: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Creates the payload for the Gemini API request.
        """
        contents = []
        for message in messages:
            contents.append({"role": "user", "parts": [{"text": message.content}]})
            if isinstance(message, HumanMessage) or isinstance(message, SystemMessage):
                contents.append({"role": "user", "parts": [{"text": message.content}]})
            elif isinstance(message, AIMessage):
                contents.append(
                    {"role": "model", "parts": [{"text": message.content}]}
                )  # Assuming 'model' role for AI messages
            # elif isinstance(message, SystemMessage):
            #     contents.append({"role": "system", "parts": [{"text": message.content}]})
            else:
                raise ValueError(f"Unsupported message type: {type(message)}")

        payload = {
            "contents": contents,
            "allowedModels": [self.model_name],
            "model": self.model_name,
            "generationConfig": {  # Add generation config
                "maxOutputTokens": self.max_tokens,
                "temperature": self.temperature,
            },
        }
        return payload

    def _create_headers(self) -> Dict[str, str]:
        """Creates the headers for the API request."""
        if not self.api_token:  # Add check in case validation somehow failed
            raise ValueError("API token is not set before creating headers.")
        token_value = self.api_token.get_secret_value()
        return {
            "Content-Type": "application/json",
            "FlowAgent": self.flow_agent,
            "FlowTenant": self.flow_tenant,
            "Authorization": f"Bearer {token_value}",
        }

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Override the _generate method to implement the chat model logic."""

        payload = self._create_payload(messages, stop)
        headers = self._create_headers()

        response = requests.post(
            self.api_url, headers=headers, json=payload, timeout=1200
        )
        response.raise_for_status()

        result = response.json()

        # Adapting to the new response format
        # Assuming the response contains 'candidates' which contain 'content'
        candidates = result.get("candidates", [])
        if candidates:
            candidate = candidates[0]
            content = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
            usage_metadata = result.get("usageMetadata", {})

            message = AIMessage(
                content=content,
                role="assistant",
                additional_kwargs={},  # Used to add additional payload to the message
                response_metadata={  # Use for response metadata
                    "model": result.get(
                        "modelVersion"
                    ),  # changed from result.get("model")
                    "finish_reason": candidate.get("finishReason"),
                    "index": candidate.get("index"),
                    "avgLogprobs": candidate.get("avgLogprobs"),
                    "createTime": result.get("createTime"),
                    "responseId": result.get("responseId"),
                    "prompt_token_count": usage_metadata.get("promptTokenCount"),
                    "completion_token_count": usage_metadata.get(
                        "candidatesTokenCount"
                    ),
                },
                usage_metadata={
                    "input_tokens": usage_metadata.get("promptTokenCount"),
                    "output_tokens": usage_metadata.get("candidatesTokenCount"),
                    "total_tokens": usage_metadata.get("totalTokenCount"),
                    "traffic_type": usage_metadata.get("trafficType"),
                    "thoughts_token_count": usage_metadata.get("thoughtsTokenCount"),
                },
            )

            generation = ChatGeneration(message=message)
            return ChatResult(generations=[generation])
        else:
            raise ValueError("No candidates found in the API response.")

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        # Add checks here too, although ideally validation should prevent this
        if not hasattr(self, "api_url") or not self.api_url:
            print("ERROR: _identifying_params called but self.api_url is missing!")
            # Optionally raise error or return placeholder
            # raise ValueError("api_url missing in _identifying_params")
            return {"error": "api_url missing"}

        return {
            "api_url": self.api_url,
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
        }
