from dotenv import load_dotenv
from .schemas import QueryState, InterviewState


# Graph Node Utilities(Planning Modules)

# NewsBot Utilities
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

# InterviewBot Utilities
def interview_tools_condition(state: InterviewState, messages_key: str = "messages") -> str:
    ai_message = None

    if isinstance(state, list):
        ai_message = state[-1]
    elif isinstance(state, dict) and (messages := state.get(messages_key, [])) or (
        messages := getattr(state, messages_key, [])
    ):
        ai_message = messages[-1]
    else:
        msg = f"No messages found in input state to tool_edge: {state}"
        raise ValueError(msg)

    if (hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0):
        return "execution_tools"
    
    return "answer_collection_node"

