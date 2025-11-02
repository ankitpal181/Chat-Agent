from typing import Annotated, TypedDict
from dotenv import load_dotenv
from .storage import Storage
from .llms import Model
from .prompts import NEWSBOT_PROMPT
from langchain_core.messages import SystemMessage, BaseMessage
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langsmith import traceable


# Load environment variables
load_dotenv()

# Graph state schema
class QueryState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# AI instances
model = Model()

# Graph Nodes
@traceable(name="query_function")
def query_function(state: QueryState) -> dict:
    messages = state["messages"]

    if len(messages) and not isinstance(messages[0], SystemMessage):
        system_prompt = SystemMessage(NEWSBOT_PROMPT)
        messages.insert(0, system_prompt)

    response = model.model.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(model.tools)


# Graph
graph = StateGraph(QueryState)

graph.add_node("query_node", query_function)
graph.add_node("tools", tool_node)

graph.add_edge(START, "query_node")
graph.add_conditional_edges("query_node", tools_condition)
graph.add_edge("tools", "query_node")

newsbot = graph.compile(Storage("database").storage)
