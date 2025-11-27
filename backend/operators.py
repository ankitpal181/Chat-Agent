import json
from .llms import Model
from .schemas import HeadlinesSchema, StoriesSchema, QueryState
from .prompts import NEWSBOT_ANCHOR_PROMPT, NEWSBOT_JOURNALIST_PROMPT, NEWSBOT_REPORTER_PROMPT
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage, HumanMessage, RemoveMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import REMOVE_ALL_MESSAGES


# AI instances
reporter_model = Model(HeadlinesSchema)
journalist_model = Model(StoriesSchema)
anchor_model = Model()


# Graph Node Operators/Functions
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
            state["messages"].insert(0, system_prompt)

    return state

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
