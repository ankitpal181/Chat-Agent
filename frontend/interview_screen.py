import streamlit as st
import json
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from backend.interview_server import interviewbot
from frontend.interview_layout import (
    render_format_selection,
    render_candidate_info,
    render_q_n_a,
    render_evaluation
)

def restore_session_state():
    # Load session state on refresh
    try:
        if "format" not in st.session_state:
            for checkpointer in interviewbot.checkpointer.list():
                interview_thread_id = checkpointer.config["configurable"]["thread_id"]
                state_values = interviewbot.get_state(
                    config=checkpointer.config["configurable"]
                ).values
                messages = state_values["messages"]

                for message in messages:
                    if isinstance(message, HumanMessage) and (
                        "name" in message.content and
                        "role" in message.content and
                        "companies" in message.content
                    ):
                        st.session_state["candidate_info"] = json.loads(message.content)
                        break
                
                st.session_state["interview_status"] = state_values.get("phase", "format-selection")
                st.session_state["q&a_config"] = checkpointer.config["configurable"]
                st.session_state["format"] = state_values["rules"]["format"]

                if "__interrupt__" in state_values:
                    st.session_state["bot_response"] = interviewbot.invoke(
                        Command(resume=""), st.session_state["q&a_config"]
                    )
                else:
                    st.session_state["bot_response"] = state_values
                break
    except:
        st.write("Failed to load session state")


def render_interview():
    # restore_session_state()
    interview_status = st.session_state.get("interview_status", "format-selection")

    if interview_status == "format-selection":
        render_format_selection()

    elif interview_status == "information-collection":
        render_candidate_info()
    
    elif interview_status == "q&a":
        render_q_n_a()
    
    elif interview_status == "evaluation":
        render_evaluation()
