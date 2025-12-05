import streamlit as st
from frontend.interview_layout import (
    render_format_selection,
    render_candidate_info,
    render_q_n_a,
    render_evaluation
)

def render_interview():
    interview_status = st.session_state.get("interview_status", "format-selection")

    if interview_status == "format-selection":
        render_format_selection()

    elif interview_status == "information-collection":
        render_candidate_info()
    
    elif interview_status == "q&a":
        render_q_n_a()
    
    elif interview_status == "evaluation":
        render_evaluation()
