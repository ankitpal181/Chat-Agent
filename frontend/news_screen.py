import streamlit as st
from backend.news_server import newsbot
from .news_layouts import render_headlines, render_stories, render_summary


def render_news():
    # States and Options
    segment = st.session_state.get("segment", "headlines")

    # Flow
    if segment == "headlines":
        render_headlines(newsbot)
    elif segment == "stories":
        render_stories(newsbot)
    else:
        render_summary(newsbot)
