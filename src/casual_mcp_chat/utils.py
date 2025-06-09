from pathlib import Path
import streamlit as st

from casual_mcp.models import ChatMessage
from casual_mcp_chat.session import Session


TEMPLATES_DIR = Path("prompt-templates")

def get_available_templates() -> list[str]:
    return [
        f.stem  # filename without .j2 extension
        for f in TEMPLATES_DIR.glob("*.j2")
    ]

def get_template_content(template_name) -> str:
    # Load the selected template content
    template_path = TEMPLATES_DIR / f"{template_name}.j2"
    template_content = template_path.read_text()
    return template_content

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
