import streamlit as st
from ui.conversation import run_conversation

def render_chat_interface():
    """Render the main chat interface."""
    # Surface any setup errors immediately (without blocking render)
    if "assistant_error" in st.session_state:
        st.warning("Assistant init error detected. It will be retried on first message.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []  # list of dicts: {"role": "user"|"assistant", "content": str}

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    prompt = st.chat_input("Ask about the weather (e.g., 'Weather at 43.7, -79.4')")
    if prompt:
        # Add user message to UI/history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Call the assistant
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = run_conversation(prompt)
            st.write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

def render_sidebar():
    """Render the sidebar with setup information."""
    with st.sidebar:
        st.header("Setup")
        st.markdown("""
        **1. Install deps**
        ```bash
        pip install streamlit python-dotenv "openai>=1.40" requests
        ```
        **2. Run locally**
        ```bash
        streamlit run app.py
        ```
        **Troubleshooting**
        - Ensure `azureopenai.env` is in the same folder and contains valid keys.
        - Replace `model` with your **Azure deployment name** (e.g., `gpt-4o-mini`).
        - If the page is blank, check your terminal for errors and try: `streamlit run app.py --server.runOnSave=false`.
        - The assistant and thread are created lazily on first message, so the page should render even if keys are missing.
        """)