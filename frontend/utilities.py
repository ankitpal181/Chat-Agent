import json
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


def set_multi_states(state_data: dict):
    # print(state_data)
    for key, value in state_data.items():
        # print(st.session_state)
        st.session_state[key] = value

def set_state(key: str, value: str):
    st.session_state[key] = value

def add_remove_state(key: str, value: str):
    st.session_state[key] = st.session_state.get(key, [])

    if value in st.session_state[key]: st.session_state[key].remove(value)
    else: st.session_state[key].append(value)

def clear_chat_history(bot, thread: int = 1, log_type: str = "chat") -> None:
    bot.checkpointer.delete_thread(thread)
    st.session_state[f"{log_type}_logs"] = []

def load_messages(
    bot, instant: bool = False, type: str = None, input: str = None, thread: int = 1,
    log_type: str = "chat"
) -> None:
    if log_type == "news": bot_state_attribute = "queries"
    else: bot_state_attribute = "messages"

    if instant:
        if type == "user": st.session_state[f"{log_type}_logs"].append({"user": input})
        else: st.session_state[f"{log_type}_logs"].append({"assistant": input})
    else:
        if f"{log_type}_logs" not in st.session_state:
            st.session_state[f"{log_type}_logs"] = []
            messages = bot.get_state({"configurable": {"thread_id": thread}}).values.get(
                bot_state_attribute, []
            )

            for message in messages:
                if isinstance(message, HumanMessage):
                    st.session_state[f"{log_type}_logs"].append({"user": message.content})
                elif isinstance(message, AIMessage) and message.content:
                    st.session_state[f"{log_type}_logs"].append({"assistant": message.content})
                elif isinstance(message, ToolMessage) and "file_path" in message.content:
                    message_content = json.loads(message.content)
                    st.session_state[f"{log_type}_logs"].append({"tool": message_content})

def publish_messages(
    bot, instant: bool = False, type: str = None, input: str = None, thread: int = 1,
    log_type: str = "chat"
) -> None:
    if log_type == "news": bot_state_attribute = "queries"
    else: bot_state_attribute = "messages"

    if instant:
        if type == "user":
            with st.chat_message("user"):
                st.text(input)
        else:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response, index = "", 0

                for message, _ in bot.stream(
                    {bot_state_attribute: [HumanMessage(input)]},
                    {"configurable": {"thread_id": thread}},
                    stream_mode="messages"
                ):
                    if isinstance(message, AIMessage) and message.content:
                        full_response += message.content
                        message_placeholder.markdown(full_response)
                    elif isinstance(message, ToolMessage) and "file_path" in message.content:
                        message_content = json.loads(message.content.replace("'", '"'))

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
        for index, message in enumerate(st.session_state[f"{log_type}_logs"]):
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
