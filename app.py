import streamlit as st
from interface.chat import render_chat_interface, render_sidebar

# =============================
# 🌤️ Weather Assistant App
# =============================

def main():
    """Main application entry point."""
    st.set_page_config(page_title="Weather Assistant", page_icon="🌤️")
    st.title("Weather Assistant 🌤️")
    
    # Render the chat interface and sidebar
    render_chat_interface()
    render_sidebar()

if __name__ == "__main__":
    main()