import json
import streamlit as st
from backend.news_server import newsbot
from utilities import load_messages, publish_messages, set_multi_states, add_remove_state, set_state
from langchain_core.messages import HumanMessage


def render_news():
    # States and Options
    segment = st.session_state.get("segment", "headlines")

    # Flow
    if segment == "headlines":
        st.title("Today's News Headlines")
        country_options = ["World", "India", "USA", "Russia", "Canada", "Japan", "China"]
        genre_options = ["All", "Sports", "Politics", "Crime", "Business", "Economy"]
        country_filter = st.session_state.get("country_filter", 0)
        genre_filter = st.session_state.get("genre_filter", 0)
        country_filter = st.selectbox("Country", country_options, country_filter)
        genre_filter = st.selectbox("Genre", genre_options, genre_filter)
        headlines_input = f"Top news headlines today. Filter: Region='{country_filter}', Genre='{genre_filter}'"
        headlines_response = st.session_state.get("headlines_response")

        if headlines_response is None or st.session_state.get("headlines_input") != headlines_input:
            with st.spinner(":hourglass: :blue[Loading Data] - :grey[Building UI Skeleton...] *Please wait patiently* :gear:"):
                headlines_response = newsbot.invoke(
                    {"messages": [HumanMessage(headlines_input)], "segment": "headlines"},
                    {"configurable": {"thread_id": 2}}
                )

        for index, headline in enumerate(json.loads(headlines_response["messages"][-1].content)["headlines"]):
            with st.container(border=True):
                info_space, button_space = st.columns([19, 1])

                with info_space:
                    st.badge(headline["location"])

                with button_space:
                    st.button(
                        "",
                        key=index,
                        on_click=set_multi_states,
                        args=[{"segment": "stories", "selected_headline": headline["text"]}],
                        type="tertiary",
                        icon=":material/fullscreen:"
                    )

                st.subheader(headline["text"])
                st.write(headline["date"])
        
        set_multi_states({
            "country_filter": country_options.index(country_filter),
            "genre_filter": genre_options.index(genre_filter),
            "headlines_response": headlines_response,
            "headlines_input": headlines_input
        })
    elif segment == "stories":
        selected_headline = st.session_state.get("selected_headline", "")
        stories_selected = st.session_state.get("stories_selected", [])
        stories_input = f"Selected Headline: {selected_headline}"
        stories_response = st.session_state.get("stories_response")

        st.title("Full Story")
        st.subheader(selected_headline)

        if stories_response is None or st.session_state.get("stories_input") != stories_input:
            with st.spinner(":hourglass: :blue[Loading Data] - :grey[Building UI Skeleton...] *Please wait patiently* :gear:"):
                stories_selected = []
                stories_response = newsbot.invoke(
                    {"messages": [HumanMessage(stories_input)], "segment": "stories"},
                    {"configurable": {"thread_id": 2}}
                )

        with st.container(horizontal=True):
            for index, story in enumerate(
                json.loads(stories_response["messages"][-1].content)["stories"]
            ):
                with st.container(border=True):
                    with st.container(horizontal=True):
                        st.checkbox(
                            "Select Story",
                            value=(index in stories_selected),
                            key=index,
                            on_change=add_remove_state,
                            args=("stories_selected", index,),
                            label_visibility="collapsed"
                        )
                        st.badge(story["source"])
                    
                    st.markdown("""
                    <style>
                    /* Targets the actual HTML <textarea> element */
                    textarea {
                        background-color: #0f1116 !important;
                        border: none !important;
                        color: #fff !important;
                        resize: none !important;
                        cursor: auto !important;
                        padding-right: 0px !important;
                        -webkit-text-fill-color: #fff !important;
                    }

                    /* Optional: Targets the label for the text area */
                    [data-baseweb="textarea"] {
                        border: none !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    st.text_area(
                        "Story Content",
                        value=story["text"],
                        height=250,
                        disabled=True,
                        label_visibility="collapsed"
                    )
                    st.caption(f"Link: {story['link']}")
        
        st.button(
            "Summarize",
            on_click=set_state,
            args=("segment", "summary",),
            width="stretch"
        )
        
        set_multi_states({
            "stories_response": stories_response,
            "stories_input": stories_input
        })
    else:
        st.title("Summarized Article")
        stories = json.loads(st.session_state["stories_response"]["messages"][-1].content)["stories"]
        stories_selected = st.session_state.get("stories_selected", [])
        summary_response = st.session_state.get("summary_response")

        if not stories_selected: stories_to_summarize = json.dumps(stories)
        else: stories_to_summarize = json.dumps([stories[index] for index in stories_selected])

        if summary_response is None or st.session_state.get("stories_summarized") != stories_to_summarize:
            with st.spinner(":hourglass: :blue[Loading Data] - :grey[Building UI Skeleton...] *Please wait patiently* :gear:"):
                summary_response = newsbot.invoke(
                    {"messages": [HumanMessage(f"Summarize these articles: {stories_to_summarize}")], "segment": "summary"},
                    {"configurable": {"thread_id": 2}}
                )

        st.text(summary_response["messages"][-1].content)
        load_messages(newsbot, thread=2, log_type="news")

        if len(summary_response["messages"]) < len(st.session_state["news_logs"]):
            publish_messages(newsbot, thread=2, log_type="news")
        
        query_input = st.chat_input("Type here...", )

        if query_input:
            load_messages(newsbot, True, "user", query_input, 2, "news")
            publish_messages(newsbot, True, "user", query_input, 2, "news")

            assistant_message = publish_messages(newsbot, True, "assistant", query_input, 2, "news")
            load_messages(newsbot, True, "assistant", assistant_message, 2, "news")
        
        set_multi_states({
            "summary_response": summary_response,
            "stories_summarized": stories_to_summarize,
        })
