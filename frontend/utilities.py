import json
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


# ============================================================================
# State Management Utilities
# ============================================================================

def set_multi_states(state_data: dict):
    """Update multiple session state values at once."""
    for key, value in state_data.items():
        st.session_state[key] = value

def set_state(key: str, value: str):
    """Update a single session state value."""
    st.session_state[key] = value

def add_remove_state(key: str, value: str):
    """Toggle a value in a list stored in session state."""
    st.session_state[key] = st.session_state.get(key, [])
    
    if value in st.session_state[key]: 
        st.session_state[key].remove(value)
    else: 
        st.session_state[key].append(value)

def clear_chat_history(bot, thread: int = 1, log_type: str = "chat") -> None:
    """Clear chat history from both the bot's checkpointer and session state."""
    bot.checkpointer.delete_thread(thread)
    st.session_state[f"{log_type}_logs"] = []


# ============================================================================
# Message Rendering Utilities
# ============================================================================

def _render_user_message(content: str):
    """Render a user message in the chat interface."""
    with st.chat_message("user"):
        st.text(content)

def _render_assistant_message(content: str):
    """Render an assistant message in the chat interface."""
    with st.chat_message("assistant"):
        st.text(content)

def _render_tool_message(tool_data: dict, index: int):
    """Render a tool message (file download button) in the chat interface."""
    with open(tool_data["file_path"]) as file:
        st.download_button(
            tool_data["label"],
            file.buffer,
            tool_data["file_name"],
            tool_data["mime"],
            f"{tool_data['label']}-{index}"
        )


# ============================================================================
# Message Loading (State Sync)
# ============================================================================

def load_messages(
    bot, 
    instant: bool = False, 
    type: str = None, 
    input: str = None, 
    thread: int = 1,
    log_type: str = "chat"
) -> None:
    """
    Load messages from bot state into session state logs.
    
    Args:
        bot: The bot instance (chatbot or newsbot)
        instant: If True, immediately append a single message to logs
        type: Message type ("user" or "assistant") when instant=True
        input: Message content when instant=True
        thread: Thread ID for the bot conversation
        log_type: Type of log ("chat" or "news")
    """
    bot_state_attribute = "queries" if log_type == "news" else "messages"
    
    if instant:
        # Instant mode: append a single message to logs
        if type == "user":
            st.session_state[f"{log_type}_logs"].append({"user": input})
        else:
            st.session_state[f"{log_type}_logs"].append({"assistant": input})
    else:
        # Initialization mode: load all messages from bot state
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


# ============================================================================
# Message Publishing (UI Rendering)
# ============================================================================

def publish_messages(
    bot, 
    instant: bool = False, 
    type: str = None, 
    input: str = None, 
    thread: int = 1,
    log_type: str = "chat"
) -> str:
    """
    Publish messages to the UI, either from logs or by streaming a new response.
    
    Args:
        bot: The bot instance (chatbot or newsbot)
        instant: If True, stream a new message; if False, render from logs
        type: Message type ("user" or "assistant") when instant=True
        input: User input to send to the bot when instant=True
        thread: Thread ID for the bot conversation
        log_type: Type of log ("chat" or "news")
    
    Returns:
        The assistant's response content (only when instant=True and type="assistant")
    """
    bot_state_attribute = "queries" if log_type == "news" else "messages"
    
    if instant:
        if type == "user":
            _render_user_message(input)
        else:
            # Stream assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                index = 0
                
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
                        
                        _render_tool_message(message_content, index)
                            )
                    
                    index += 1
                
            return full_response
    else:
        # Render all messages from logs
        for index, message in enumerate(st.session_state[f"{log_type}_logs"]):
            if "user" in message:
                _render_user_message(message["user"])
            elif "assistant" in message:
                _render_assistant_message(message["assistant"])
            elif "tool" in message:
                _render_tool_message(message["tool"], index)
