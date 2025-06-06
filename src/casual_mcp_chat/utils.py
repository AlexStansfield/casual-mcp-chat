import streamlit as st

from casual_mcp.models import ChatMessage
from casual_mcp_chat.session import Session


def create_new_session(
    model: str | None = None,
    system_prompt: str | None = None
):
    session_id = f"chat-{len(st.session_state.sessions) + 1}"
    st.session_state.active_session = session_id
    st.session_state.sessions[session_id] = Session(
        model=model,
        system_prompt=system_prompt
    )

def handle_chat_message(message: ChatMessage, show_tool_calls: bool = False):
    if not message.role in ['user', 'assistant']:
        return

    if message.role == 'assistant' and message.tool_calls:
        if not show_tool_calls:
            return
        
        for tool_call in message.tool_calls:
            with st.chat_message(message.role):
                st.markdown(f"Calling Tool: `{tool_call.function.name}`")
                if tool_call.function.arguments:
                    st.markdown("Arguments:")
                    st.json(tool_call.function.arguments)
        
        return

    with st.chat_message(message.role):
            st.markdown(message.content)
