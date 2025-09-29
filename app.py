import streamlit as st
from interface.chat import render_chat_interface, render_sidebar, render_architecture_page

def main():
    """Main application entry point."""
    st.set_page_config(page_title="Vision Bot", page_icon="👁️")
    st.title("Vision Bot 👁️ 👁️")
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Chat", "How It Was Built"])
    
    with tab1:
        # Render the chat interface and sidebar
        render_chat_interface()
        render_sidebar()
    
    with tab2:
        # Render the architecture page
        render_architecture_page()

if __name__ == "__main__":
    main()