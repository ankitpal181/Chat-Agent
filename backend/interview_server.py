# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from .storage import Storage
from .schemas import InterviewState
from .operators import (
    interview_perception_function, candidate_information_collection_function, question_generation_function,
    answer_collection_function, evaluation_function, tool_node
)
from .utilities import interview_tools_condition
from langgraph.graph import StateGraph, START, END


# Graph
graph = StateGraph(InterviewState)

# Graph Nodes
graph.add_node("perception_node", interview_perception_function)
graph.add_node("candidate_information_collection_node", candidate_information_collection_function)
graph.add_node("question_generation_node", question_generation_function)
graph.add_node("answer_collection_node", answer_collection_function)
graph.add_node("evaluation_node", evaluation_function)
graph.add_node("tools", tool_node)

# Graph Edges
graph.add_edge(START, "perception_node")
graph.add_edge("perception_node", "candidate_information_collection_node")
graph.add_edge("candidate_information_collection_node", "question_generation_node")
graph.add_conditional_edges("question_generation_node", interview_tools_condition)
graph.add_edge("tools", "question_generation_node")
graph.add_edge("answer_collection_node", "evaluation_node")
graph.add_edge("evaluation_node", END)

# Compile Graph
interviewbot = graph.compile(Storage("memory").storage)
