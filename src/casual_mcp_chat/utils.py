import streamlit as st

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
