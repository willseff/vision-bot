import streamlit as st
from interface.chat import render_chat_interface, render_sidebar

# =============================
# 🌤️ Vision Assistant App
# =============================

def main():
    """Main application entry point."""
    st.set_page_config(page_title="Vision Assistant", page_icon="👁️")
    st.title("Vision Assistant 👁️")
    
    # Render the chat interface and sidebar
    render_chat_interface()
    render_sidebar()

if __name__ == "__main__":
    main()