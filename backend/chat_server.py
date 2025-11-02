from typing import Annotated, TypedDict
from dotenv import load_dotenv
from .storage import Storage
from .llms import Model
from .prompts import CHATBOT_PROMPT
from langchain_core.messages import SystemMessage, BaseMessage
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langsmith import traceable


# Load environment variables
load_dotenv()

# Graph state schema
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# AI instances
model = Model()

# Graph Nodes
@traceable(name="chat_function")
def chat_function(state: ChatState) -> dict:
    messages = state["messages"]

    if len(messages) and not isinstance(messages[0], SystemMessage):
        system_prompt = SystemMessage(CHATBOT_PROMPT)
        messages.insert(0, system_prompt)

    response = model.model.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(model.tools)


# Graph
graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_function)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

chatbot = graph.compile(Storage("database").storage)
