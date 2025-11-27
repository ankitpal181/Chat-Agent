import sys
import os

# add the parent directory (project root) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import streamlit as st
from chat_screen import render_chat
from news_screen import render_news
from backend.chat_server import chatbot
from backend.news_server import newsbot
from utilities import set_state, publish_messages, clear_chat_history


# States and Options
screen = st.session_state.get("screen", "chatbot")
segment = st.session_state.get("segment", "headlines")

with st.sidebar:
    st.button("Chat", width="stretch", on_click=set_state, args=("screen", "chatbot"))
    st.button("News", width="stretch", on_click=set_state, args=("screen", "newsbot"))
    st.button("Interview", width="stretch", on_click=set_state, args=("screen", "interviewbot"))
    st.divider(width="stretch")

    if screen == "newsbot":
        if segment == "stories":
            st.button("Headlines", width="stretch", on_click=set_state, args=("segment", "headlines"))
        elif segment == "summary":
            st.button("Headlines", width="stretch", on_click=set_state, args=("segment", "headlines"))
            st.button("Stories", width="stretch", on_click=set_state, args=("segment", "stories"))
            st.button(
                "Create PDF Report",
                width="stretch",
                on_click=publish_messages,
                args=(newsbot, True, "assistant", "Generate a pdf with all the data", 2, "news")
            )
            st.button(
                "Create CSV Report",
                width="stretch",
                on_click=publish_messages,
                args=(newsbot, True, "assistant", "Generate a csv with all the data", 2, "news")
            )
    elif screen == "chatbot":
        st.button("New Chat", width="stretch", on_click=clear_chat_history, args=(chatbot,))
        st.button(
            "Create PDF Report",
            width="stretch",
            on_click=publish_messages,
            args=(chatbot, True, "assistant", "Generate a pdf with all the data")
        )
        st.button(
            "Create CSV Report",
            width="stretch",
            on_click=publish_messages,
            args=(chatbot, True, "assistant", "Generate a csv with all the data")
        )


# Flow
if screen == "chatbot":
    render_chat()
elif screen == "newsbot":
    render_news()
else:
    pass
