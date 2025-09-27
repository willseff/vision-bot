import streamlit as st
import base64
from interface.conversation import run_conversation

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

    # Image upload
    uploaded_file = st.file_uploader("Upload an image (optional)", type=["jpg", "jpeg", "png", "bmp", "gif"])
    
    # Chat input
    prompt = st.chat_input("Ask about the weather or upload an image for analysis")
    if prompt:
        # Prepare message content
        message_content = prompt
        
        # Handle uploaded image
        image_data = None
        if uploaded_file is not None:
            # Read and encode image
            image_bytes = uploaded_file.read()
            image_data = base64.b64encode(image_bytes).decode('utf-8')
            message_content += f"\n\n[Image uploaded: {uploaded_file.name}] Please analyze this image and provide smart cropping suggestions."
        
        # Add user message to UI/history
        st.session_state.messages.append({"role": "user", "content": message_content})
        with st.chat_message("user"):
            st.write(message_content)
            if uploaded_file is not None:
                st.image(uploaded_file, caption=uploaded_file.name, width=300)

        # Call the assistant
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = run_conversation(message_content, image_data=image_data)
            
            # Display the assistant's text response
            st.write(reply)
            
            # Check if there's a cropped image to display
            if "cropped_image_data" in st.session_state:
                crop_data = st.session_state.cropped_image_data
                st.image(f"data:image/jpeg;base64,{crop_data['cropped_image_b64']}", 
                       caption=f"Cropped image ({crop_data['cropped_size']['width']}x{crop_data['cropped_size']['height']})",
                       width=300)
                st.success("✅ Image cropped successfully!")
                # Clear the cropped image data after displaying
                del st.session_state.cropped_image_data
                
        st.session_state.messages.append({"role": "assistant", "content": reply})

def render_sidebar():
    """Render the sidebar with setup information."""
    with st.sidebar:
        st.header("Setup")
        st.markdown("""
        **1. Install deps**
        ```bash
        pip install streamlit python-dotenv "openai>=1.40" requests azure-ai-vision azure-core
        ```
        **2. Run locally**
        ```bash
        streamlit run app.py
        ```
        **Features**
        - Chat with AI assistant
        - Get weather information
        - Upload images for smart cropping analysis and actual cropping
        
        **Troubleshooting**
        - Ensure `azureopenai.env` contains valid Azure OpenAI and Vision API keys.
        - Replace `model` with your **Azure deployment name** (e.g., `gpt-4o-mini`).
        - If the page is blank, check your terminal for errors and try: `streamlit run app.py --server.runOnSave=false`.
        - The assistant and thread are created lazily on first message, so the page should render even if keys are missing.
        """)