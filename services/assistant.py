import streamlit as st
from services.azure_client import get_azure_openai_client
from tools.registry import TOOLS_LIST
from config.settings import Config

def ensure_assistant_and_thread():
    """Create assistant/thread only when first needed to avoid blank page on load."""
    client = get_azure_openai_client()

    if "assistant_id" not in st.session_state:
        try:
            with st.spinner("Setting up assistant..."):
                assistant = client.beta.assistants.create(
                    name=Config.ASSISTANT_NAME,
                    instructions=Config.ASSISTANT_INSTRUCTIONS,
                    tools=TOOLS_LIST,
                    model=Config.AZURE_OPENAI_MODEL,
                )
                st.session_state.assistant_id = assistant.id
        except Exception as e:
            st.session_state.assistant_error = str(e)

    if "thread_id" not in st.session_state and "assistant_id" in st.session_state:
        try:
            thread = client.beta.threads.create()
            st.session_state.thread_id = thread.id
        except Exception as e:
            st.session_state.assistant_error = str(e)