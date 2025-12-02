# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from .storage import Storage
from .schemas import QueryState
from .operators import news_perception_function, headlines_function, stories_function, query_function, custom_tool_node
from .utilities import select_segment_function, custom_tools_condition
from langgraph.graph import StateGraph, START


# Graph
graph = StateGraph(QueryState)

# Graph Nodes
graph.add_node("perception_node", news_perception_function)
graph.add_node("headlines_node", headlines_function)
graph.add_node("stories_node", stories_function)
graph.add_node("query_node", query_function)
graph.add_node("tools", custom_tool_node)

# Graph Edges
graph.add_edge(START, "perception_node")
graph.add_conditional_edges("perception_node", select_segment_function)
graph.add_conditional_edges("headlines_node", custom_tools_condition)
graph.add_conditional_edges("stories_node", custom_tools_condition)
graph.add_conditional_edges("query_node", custom_tools_condition)
graph.add_edge("tools", "perception_node")

# Compile Graph
newsbot = graph.compile(Storage("memory").storage)
