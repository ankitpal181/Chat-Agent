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
from utilities import convert_state_snapshot, stop_audio_recording

def restore_session_state():
    # Load session state on refresh
    try:
        interview_thread_id = st.query_params.get("thread_id")
        if interview_thread_id and "format" not in st.session_state:
            with st.spinner("Restoring Session State..."):
                st.session_state["q&a_config"] = {"configurable": {"thread_id": interview_thread_id}}
                snapshot = interviewbot.get_state(
                    config=st.session_state["q&a_config"]
                )
                state_values = convert_state_snapshot(snapshot)
                
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
                st.session_state["format"] = state_values["rules"]["format"]

                if "__interrupt__" in state_values:
                    stop_audio_recording()
                    st.session_state["bot_response"] = interviewbot.invoke(
                        Command(resume=""), st.session_state["q&a_config"]
                    )
                else:
                    st.session_state["bot_response"] = state_values
    except Exception as ex:
        st.write("Failed to load session state")


def render_interview():
    restore_session_state()
    interview_status = st.session_state.get("interview_status", "format-selection")

    if interview_status == "format-selection":
        render_format_selection()

    elif interview_status == "information-collection":
        render_candidate_info()
    
    elif interview_status == "q&a":
        render_q_n_a()
    
    elif interview_status == "evaluation":
        render_evaluation()
