from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from typing import Annotated, Callable, Sequence, TypedDict, Union
import operator
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    AnyMessage,
)
from langchain_core.language_models import BaseChatModel
from generativeai.prompter_interface import PrompterInterface
from typing import Any, Callable, Union, Dict
from collections.abc import Sequence
from langchain_core.tools import BaseTool
from langchain_core.tools import tool


@tool
def get_wheter(city_name: Annotated[str, "City name"]) -> str:
    """use this tool to get the current weather for a given city."""
    return f"The weather in {city_name} is sunny with a temperature of 25°C."


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class LangGraphAgent:
    def __init__(
        self,
        prompter: PrompterInterface,
        tools: Sequence[Union[Dict[str, Any], type, Callable, BaseTool]] = [get_wheter],
        system_message: str = "",
    ) -> None:
        self.prompter = prompter
        self.system_message = system_message
        self.graph: CompiledStateGraph = self.__build_graph()
        self.tools = self.__map_tools(tools)
        self.prompter.bind_tools(tools)

    def start_graph(self, messages: list[BaseMessage]) -> str:
        result = self.graph.invoke({"messages": messages})
        return result["messages"][-1].content

    def __invoke_llm(self, state: AgentState):
        messages = state["messages"]

        if self.system_message:
            messages = [SystemMessage(content=self.system_message)] + messages

        message = self.prompter.invoke_llm_with_messages(messages)
        return {"messages": [message]}

    def __take_action(self, state: AgentState):
        tool_calls = state["messages"][-1].tool_calls
        results = []

        for t in tool_calls:
            print("Executing tool:", t)
            result = self.tools[t["name"]].invoke(t["args"])
            results.append(
                ToolMessage(content=result, tool_call_id=t["id"], name=t["name"])
            )

        print("Back to the model!!")
        return {"messages": results}

    def __exists_action(self, state: AgentState):
        result = state["messages"][-1]
        return len(result.tool_calls) > 0

    def __build_graph(self) -> CompiledStateGraph:
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.__invoke_llm)
        graph.add_node("action", self.__take_action)
        graph.add_conditional_edges(
            "llm", self.__exists_action, {True: "action", False: END}
        )
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")

        return graph.compile()

    def __map_tools(
        self, tools: Sequence[Union[Dict[str, Any], type, Callable, BaseTool]]
    ) -> None:
        return {t.name: t for t in tools}
