import streamlit as st
from backend.chat_server import chatbot
from utilities import load_messages, publish_messages


# Flow
def render_chat():
    load_messages(chatbot)
    publish_messages(chatbot)

    user_input = st.chat_input("Type here...", )

    if user_input:
        load_messages(chatbot, True, "user", user_input)
        publish_messages(chatbot, True, "user", user_input)

        assistant_message = publish_messages(chatbot, True, "assistant", user_input)
        load_messages(chatbot, True, "assistant", assistant_message)
