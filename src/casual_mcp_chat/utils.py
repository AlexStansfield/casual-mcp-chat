import shutil
from pathlib import Path

import streamlit as st
from casual_mcp.models import ChatMessage

from casual_mcp_chat.session import Session

FILES_DIR = Path(__file__).parent / "files"

TEMPLATES_DIR = Path("prompt-templates")


def ensure_default_files() -> None:
    """Ensure default config and templates exist in the current directory."""
    if not TEMPLATES_DIR.exists():
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(FILES_DIR / "default.j2", TEMPLATES_DIR / "default.j2")

    config_path = Path("casual_mcp_config.json")
    if not config_path.exists():
        shutil.copy(FILES_DIR / "casual_mcp_config.json", config_path)

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
    system_prompt: str | None = None,
    prompt_name: str | None = None,
):
    session_id = f"chat-{len(st.session_state.sessions) + 1}"
    st.session_state.active_session = session_id
    st.session_state.sessions[session_id] = Session(
        model=model,
        system_prompt=system_prompt,
        prompt_name=prompt_name,
    )

def handle_chat_message(message: ChatMessage, show_tool_calls: bool = False):
    if message.role not in ['user', 'assistant']:
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
