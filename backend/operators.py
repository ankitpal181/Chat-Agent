import json
from .llms import Model
from .schemas import (
    HeadlinesSchema, StoriesSchema, QueryState, InterviewState, QuestionsSchema, EvaluationSchema
)
from .prompts import NEWSBOT_ANCHOR_PROMPT, NEWSBOT_JOURNALIST_PROMPT, NEWSBOT_REPORTER_PROMPT, INTERVIEWBOT_PROMPT
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage, HumanMessage, RemoveMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.types import interrupt


# NewsBot AI instances
reporter_model = Model(HeadlinesSchema)
journalist_model = Model(StoriesSchema)
anchor_model = Model()

# InterviewBot AI instances
questioner_model = Model(QuestionsSchema)
evaluator_model = Model(EvaluationSchema)
reporting_model = Model()


# Graph Node Operators/Functions
tool_node = ToolNode(reporter_model.tools)
reporting_tool_node = ToolNode(reporting_model.tools)

# NewsBot Functions
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

def news_perception_function(state: QueryState) -> dict:
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


# InterviewBot Functions
def candidate_information_collection_function(state: InterviewState) -> dict:
    user_name = interrupt("Please enter your full name")
    user_desired_role = interrupt("Job role you want to interview for")
    user_preferred_companies = interrupt("Please enter comma separated names of companies you prefer")
    user_information = json.dumps({
        "name": user_name,
        "role": user_desired_role,
        "companies": user_preferred_companies
    })

    return {"messages": [HumanMessage(user_information)]}

def question_generation_function(state: InterviewState) -> dict:
    messages = state["messages"]
    questions = questioner_model.model.invoke(messages)
    questions_json = questions.model_dump_json(indent = 2)

    return {"messages": [AIMessage(questions_json)], "questions": questions.questions}

def answer_collection_function(state: InterviewState) -> dict:
    questions = state["questions"]
    answers = []

    for question in questions:
        answer = interrupt(question)
        answers.append({"question": question.question, "answer": answer})
    
    return {"messages": [HumanMessage(json.dumps(answers))], "answers": answers}

def evaluation_function(state: InterviewState) -> dict:
    messages = state["messages"]
    evaluation = evaluator_model.model.invoke(messages)
    evaluation_json = evaluation.model_dump_json(indent = 2)

    return {"messages": [AIMessage(evaluation_json)]}

def interview_perception_function(state: InterviewState) -> dict:
    messages = state["messages"]
    rules = state.get("rules", {})
    user_information = json.loads(messages[1].content)
    system_prompt = SystemMessage(INTERVIEWBOT_PROMPT.format(
        role=user_information["role"],
        companies=user_information["companies"],
        time_frame=rules.get("time_frame", "1 minute"),
        no_of_questions=rules.get("no_of_questions", "5")
    ))

    if system_prompt: state["messages"].insert(0, system_prompt)

    return state

def phase_router_function(state: InterviewState) -> str:
    if state.get("phase") == "execution": return "perception_node"
    else: return "reporting_node"

def reporting_function(state: InterviewState) -> dict:
    messages = state["messages"]
    response = reporting_model.model.invoke(messages)
    return {"messages": [response]}
