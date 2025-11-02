import sys
import os

# add the parent directory (project root) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import json
import streamlit as st
from backend.news_server import newsbot
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


# Utilities
def load_messages(instant: bool = False, type: str = None, input: str = None) -> None:
    if instant:
        if type == "user": st.session_state["news_logs"].append({"user": input})
        else: st.session_state["news_logs"].append({"assistant": input})
    else:
        if "news_logs" not in st.session_state:
            st.session_state["news_logs"] = []
            messages = newsbot.get_state({"configurable": {"thread_id": 2}}).values.get("messages", [])

            for message in messages:
                if isinstance(message, HumanMessage):
                    st.session_state["news_logs"].append({"user": message.content})
                elif isinstance(message, AIMessage) and message.content:
                    st.session_state["news_logs"].append({"assistant": message.content})
                elif isinstance(message, ToolMessage) and "file_path" in message.content:
                    message_content = json.loads(message.content)
                    st.session_state["news_logs"].append({"tool": message_content})

def publish_messages(instant: bool = False, type: str = None, input: str = None) -> None:
    if instant:
        if type == "user":
            with st.chat_message("user"):
                st.text(user_input)
        else:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response, index = "", 0

                for message, _ in newsbot.stream(
                    {"messages": [HumanMessage(user_input)]},
                    {"configurable": {"thread_id": 2}},
                    stream_mode="messages"
                ):
                    if isinstance(message, AIMessage) and message.content:
                        full_response += message.content
                        message_placeholder.markdown(full_response)
                    elif isinstance(message, ToolMessage) and "file_path" in message.content:
                        message_content = json.loads(message.content)

                        with open(message_content["file_path"]) as file:
                            st.download_button(
                                message_content["label"],
                                file.buffer,
                                message_content["file_name"],
                                message_content["mime"],
                                "{}-{}".format(message_content["label"], index)
                            )
                    
                    assistant_message = full_response
                    index += 1
            return assistant_message
    else:
        for index, message in enumerate(st.session_state["news_logs"]):
            if "user" in message:
                with st.chat_message("user"):
                    st.text(message["user"])
            elif "assistant" in  message:
                with st.chat_message("assistant"):
                    st.text(message["assistant"])
            elif "tool" in message:
                with open(message["tool"]["file_path"]) as file:
                    st.download_button(
                        message["tool"]["label"],
                        file.buffer,
                        message["tool"]["file_name"],
                        message["tool"]["mime"],
                        "{}-{}".format(message["tool"]["label"], index)
                    )


# Flow
load_messages()
publish_messages()

user_input = st.chat_input("Type here...", )

if user_input:
    load_messages(True, "user", user_input)
    publish_messages(True, "user", user_input)

    assistant_message = publish_messages(True, "assistant", user_input)
    load_messages(True, "assistant", assistant_message)
