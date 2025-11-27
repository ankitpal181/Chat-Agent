import json
from typing import Annotated, TypedDict, List
from dotenv import load_dotenv
from .storage import Storage
from .llms import Model
from .prompts import NEWSBOT_ANCHOR_PROMPT, NEWSBOT_JOURNALIST_PROMPT, NEWSBOT_REPORTER_PROMPT
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage, ToolMessage, HumanMessage, RemoveMessage
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages, REMOVE_ALL_MESSAGES


# Load environment variables
load_dotenv()

# Graph state and output schemas
class QueryState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    segment: str
    queries: Annotated[list[BaseMessage], add_messages]

class HeadlinesItemSchema(BaseModel):
    location: str = Field(
        description = "Location of where the incident/event of a single news headline took place"
    )
    text: str = Field(
        description = "Text of a single news headline"
    )
    date: str = Field(
        description = "Date & time, in human readble format, of when the incident/event of a single news headline took place"
    )

class StoriesItemSchema(BaseModel):
    source: str = Field(
        description = "Name of source of the article"
    )
    text: str = Field(
        description = "Text/Content of the article"
    )
    link: str = Field(
        description = "http/hhtps link of the article's full story"
    )

class HeadlinesSchema(BaseModel):
    headlines: List[HeadlinesItemSchema] = Field(description = "List of news headlines")

class StoriesSchema(BaseModel):
    stories: List[StoriesItemSchema] = Field(description = "List of selected headline related articles")

# AI instances
reporter_model = Model(HeadlinesSchema)
journalist_model = Model(StoriesSchema)
anchor_model = Model()

# Graph Nodes
tool_node = ToolNode(reporter_model.tools)

def headlines_function(state: QueryState) -> dict:
    messages = state["messages"]
    headlines = reporter_model.model.invoke(messages)
    headlines_json = headlines.model_dump_json(indent = 2)

    return {"messages": [AIMessage(headlines_json)]}

def stories_function(state: QueryState) -> dict:
    messages = state["messages"]
    stories = journalist_model.model.invoke(messages)
    stories_json = stories.model_dump_json(indent = 2)

    return {"messages": [AIMessage(stories_json)]}

def query_function(state: QueryState) -> dict:
    messages = state["messages"]
    queries = state.get("queries", [])

    if not queries or isinstance(messages[-1], HumanMessage):
        response = anchor_model.model.invoke(messages)
        return {"messages": [response], "queries": [messages[-1], response]}
    else:
        response = anchor_model.model.invoke(queries)
        return {"queries": [response]}

def perception_function(state: QueryState) -> dict:
    messages = state["messages"]
    queries = state.get("queries", [])
    segment = state.get("segment", "")
    system_prompt = None

    if segment == "headlines":
        system_prompt = SystemMessage(NEWSBOT_REPORTER_PROMPT)
    elif segment == "stories":
        system_prompt = SystemMessage(NEWSBOT_JOURNALIST_PROMPT)
    elif segment == "summary":
        system_prompt = SystemMessage(NEWSBOT_ANCHOR_PROMPT)
        
        if isinstance(messages[-1], ToolMessage):
            state["queries"].append(messages[-1])
        
        if not queries or isinstance(messages[-1], HumanMessage):
            state["queries"].append(RemoveMessage(id=REMOVE_ALL_MESSAGES))

    if system_prompt:
        if not messages or messages[0].content != system_prompt.content:
            return {"messages": [system_prompt]}

    return state

def select_segment_function(state: QueryState) -> str:
    if "segment" in state:
        if state["segment"] == "headlines": return "headlines_node"
        elif state["segment"] == "stories": return "stories_node"
        else: return "query_node"
    else: return "query_node"

def custom_tools_condition(
    state: QueryState, messages_key: str = "messages", queries_key: str = "queries"
) -> str:
    ai_message = None
    query_ai_message = None

    if isinstance(state, list):
        ai_message = state[-1]
    elif isinstance(state, dict):
        if (messages := state.get(messages_key, [])) or (messages := getattr(state, messages_key, [])):
            ai_message = messages[-1]

        if (queries := state.get(queries_key, [])) or (queries := getattr(state, queries_key, [])):
            query_ai_message = queries[-1]
    else:
        msg = f"No messages found in input state to tool_edge: {state}"
        raise ValueError(msg)

    if (hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0) or (
        hasattr(query_ai_message, "tool_calls") and len(query_ai_message.tool_calls) > 0
    ):
        return "tools"
    
    return "__end__"

def custom_tool_node(state: QueryState) -> dict:
    if "queries" in state:
        last_message = state["queries"][-1]

        if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
            tool_messages = []

            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_to_run = reporter_model.tools_by_name[tool_name]
                result = tool_to_run.invoke(tool_call["args"])
                if isinstance(result, dict) or isinstance(result, list): result = json.dumps(result, indent=2)
                tool_messages.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))

            return {"queries": tool_messages}

    return tool_node.invoke(state)


# Graph
graph = StateGraph(QueryState)

graph.add_node("perception_node", perception_function)
graph.add_node("headlines_node", headlines_function)
graph.add_node("stories_node", stories_function)
graph.add_node("query_node", query_function)
graph.add_node("tools", custom_tool_node)

graph.add_edge(START, "perception_node")
graph.add_conditional_edges("perception_node", select_segment_function)
graph.add_conditional_edges("headlines_node", custom_tools_condition)
graph.add_conditional_edges("stories_node", custom_tools_condition)
graph.add_conditional_edges("query_node", custom_tools_condition)
graph.add_edge("tools", "perception_node")

newsbot = graph.compile(Storage("memory").storage)
