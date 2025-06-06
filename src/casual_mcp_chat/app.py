import asyncio

import streamlit as st
from casual_mcp import McpToolChat, ProviderFactory, load_config, load_mcp_client
from casual_mcp.models import UserMessage
from dotenv import load_dotenv

from casual_mcp_chat.session import Session
from casual_mcp_chat.utils import create_new_session, handle_chat_message

default_system_prompt = """You are a helpful assistant.

You have access to up-to-date information through the tools, but you must never mention that tools were used.

Respond naturally and confidently, as if you already know all the facts.

**Never mention your knowledge cutoff, training data, or when you were last updated.**

You must not speculate or guess about dates — if a date is given to you by a tool, assume it is correct and respond accordingly without disclaimers.

Always present information as current and factual.
"""

# Load configs + providers
load_dotenv()
config = load_config("casual_mcp_config.json")
mcp_client = load_mcp_client(config)
provider_factory = ProviderFactory(mcp_client)

st.title("🧠 Casual MCP Chat")

# Initialize session storage
if "sessions" not in st.session_state:
    st.session_state.sessions = {}

if "active_session" not in st.session_state:
    create_new_session(system_prompt=default_system_prompt)

# Get current session
session: Session = st.session_state.sessions[st.session_state.active_session]

# Sidebar: session controls
st.sidebar.title("💬 Sessions")

# New Chat button
if st.sidebar.button("➕ New Chat", use_container_width=True):
    create_new_session(
        model=session.model,
        system_prompt=session.system_prompt
    )
    st.rerun()

# List existing sessions
for session_id in list(st.session_state.sessions.keys()):
    cols = st.sidebar.columns([3, 1])
    with cols[0]:
        label = f"✨ {session_id}" if session_id == st.session_state.active_session else session_id
        if st.button(label, use_container_width=True):
            st.session_state.active_session = session_id
            st.rerun()
    with cols[1]:
        if st.button("❌", key=f"delete-{session_id}", use_container_width=True):
            del st.session_state.sessions[session_id]
            if session_id == st.session_state.active_session:
                # Switch to another or create new
                if st.session_state.sessions:
                    st.session_state.active_session = next(iter(st.session_state.sessions))
                else:
                    create_new_session(system_prompt=default_system_prompt)
            st.rerun()

st.sidebar.markdown("---")

# Select model
model = st.sidebar.selectbox(
    "Model",
    [key for key in config.models.keys()],
    index=list(config.models.keys()).index(session.model) if session.model else 0,
)

if model != session.model:
    session.model = model

# System prompt editor
session.system_prompt = st.sidebar.text_area(
    "System Prompt",
    session.system_prompt,
    height=300,
)

# Toggle tool calls (future feature)
show_tool_calls = st.sidebar.checkbox("Show Tool Calls", value=False)

async def main():
    # Display chat history
    for message in session.messages:
        handle_chat_message(message, show_tool_calls)

    # Handle new user input
    if prompt := st.chat_input("How can I help?"):
        provider = await provider_factory.get_provider(
            session.model,
            config.models[session.model]
        )
        chat = McpToolChat(
            mcp_client,
            provider,
            session.system_prompt
        )

        # Generate User Message, add to session and display
        user_message = UserMessage(content=prompt)
        session.messages.append(user_message)
        handle_chat_message(user_message)

        # Run tool-calling chat loop
        response_messages = await chat.chat(
            session.messages.copy(),
        )

        # Display assistant responses + store them
        for message in response_messages:
            handle_chat_message(message, show_tool_calls)

        session.messages.extend(response_messages)

asyncio.run(main())
