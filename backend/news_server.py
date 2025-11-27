from typing import Annotated, TypedDict, List
from dotenv import load_dotenv
from .storage import Storage
from .llms import Model
from .prompts import NEWSBOT_ANCHOR_PROMPT, NEWSBOT_JOURNALIST_PROMPT, NEWSBOT_REPORTER_PROMPT
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage, ToolMessage
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages


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
def headlines_function(state: QueryState) -> dict:
    messages = state["messages"]
    
    if len(messages) and not isinstance(messages[0], SystemMessage):
        system_prompt = SystemMessage(NEWSBOT_REPORTER_PROMPT)
        messages.insert(0, system_prompt)

    headlines = reporter_model.model.invoke(messages)
    headlines_json = headlines.model_dump_json(indent = 2)
    return {"messages": [AIMessage(headlines_json)]}

def stories_function(state: QueryState) -> dict:
    messages = state["messages"]

    if len(messages) and not isinstance(messages[0], SystemMessage):
        system_prompt = SystemMessage(NEWSBOT_JOURNALIST_PROMPT)
        messages.insert(0, system_prompt)

    stories = journalist_model.model.invoke(messages)
    stories_json = stories.model_dump_json(indent = 2)
    return {"messages": [AIMessage(stories_json)]}

def query_function(state: QueryState) -> dict:
    messages = state["messages"]
    queries = state.get("queries", [])

    if len(messages) and not isinstance(messages[0], SystemMessage):
        system_prompt = SystemMessage(NEWSBOT_ANCHOR_PROMPT)
        messages.insert(0, system_prompt)

    if not queries:
        response = anchor_model.model.invoke(messages)
        return {"messages": [response], "queries": [messages[-1], response]}
    else:
        response = anchor_model.model.invoke(queries)
        return {"queries": [response]}

def  router_function(state: QueryState) -> dict:
    if state["segment"] == "summary" and isinstance(state["messages"][-1], ToolMessage):
        state["queries"].append(state["messages"][-1])
    return state

def select_segment_function(state: QueryState) -> str:
    if "segment" in state:
        if state["segment"] == "headlines": return "headlines_node"
        elif state["segment"] == "stories": return "stories_node"
        else: return "query_node"
    else: return "query_node"

tool_node = ToolNode(reporter_model.tools)


# Graph
graph = StateGraph(QueryState)

graph.add_node("headlines_node", headlines_function)
graph.add_node("stories_node", stories_function)
graph.add_node("query_node", query_function)
graph.add_node("tools", tool_node)
graph.add_node("router_node", router_function)

graph.add_edge(START, "router_node")
graph.add_conditional_edges("router_node", select_segment_function)
graph.add_conditional_edges("headlines_node", tools_condition)
graph.add_conditional_edges("stories_node", tools_condition)
graph.add_conditional_edges("query_node", tools_condition)
graph.add_edge("tools", "router_node")

newsbot = graph.compile(Storage("memory").storage)
