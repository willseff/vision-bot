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
    
    # Initialize upload key for file uploader
    if "upload_key" not in st.session_state:
        st.session_state.upload_key = 0
    
    # Render chat history FIRST
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
            # For user messages with images, display the image
            if msg["role"] == "user" and "image_data" in msg:
                try:
                    image_bytes = base64.b64decode(msg["image_data"])
                    st.image(image_bytes, caption="Uploaded image", width=300)
                except:
                    pass
            
            # For assistant messages with cropped images, display the cropped image
            if msg["role"] == "assistant" and "cropped_image_data" in msg:
                crop_data = msg["cropped_image_data"]
                st.image(f"data:image/jpeg;base64,{crop_data['cropped_image_b64']}", 
                       caption=f"Cropped image ({crop_data['cropped_size']['width']}x{crop_data['cropped_size']['height']})",
                       width=300)
                st.success("Image cropped successfully!")
            
            # For assistant messages with upscaled images, display the upscaled image
            if msg["role"] == "assistant" and "upscaled_image_data" in msg:
                upscale_data = msg["upscaled_image_data"]
                scale = upscale_data.get('scale_factor', 'unknown')
                new_size = upscale_data.get('upscaled_size', {})
                width = new_size.get('width', 'unknown')
                height = new_size.get('height', 'unknown')
                st.image(f"data:image/png;base64,{upscale_data['upscaled_image_b64']}", 
                       caption=f"Upscaled {scale}x ({width}x{height}) - Enhanced with OpenCV EDSR",
                       width=400)  # Larger display for upscaled images
                st.success(f"Image upscaled {scale}x successfully using OpenCV EDSR model!")

    # Check if we're currently processing a message (show spinner below messages, above input)
    if "processing" in st.session_state and st.session_state.processing:
        # Show spinner below chat history but above input controls
        with st.spinner("Thinking..."):
            # Get the message data from session state
            message_content = st.session_state.pending_message
            image_data = st.session_state.get("pending_image_data")
            
            # Call the assistant and add response to history
            response = run_conversation(message_content, image_data=image_data)
            
            # Add assistant message to history (include image data if present)
            assistant_message = {"role": "assistant", "content": response["content"]}
            if "cropped_image_data" in response:
                assistant_message["cropped_image_data"] = response["cropped_image_data"]
            if "upscaled_image_data" in response:
                assistant_message["upscaled_image_data"] = response["upscaled_image_data"]
            st.session_state.messages.append(assistant_message)
            
            # Clear processing state
            del st.session_state.processing
            del st.session_state.pending_message
            if "pending_image_data" in st.session_state:
                del st.session_state.pending_image_data
            
            # Rerun to update the display
            st.rerun()
    
    # Create input controls at the BOTTOM (only when not processing)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat input
        prompt = st.chat_input("Ask about the weather or upload an image for analysis")
    
    with col2:
        # Image upload (in a column next to chat input)
        # Use a unique key to reset after each upload
        upload_key = st.session_state.get("upload_key", 0)
        uploaded_file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "bmp", "gif"], 
                                       label_visibility="collapsed", key=f"uploader_{upload_key}")
    
    # Process input AFTER rendering everything else
    if prompt:
        # Prepare message content (keep user's original message clean)
        message_content = prompt
        
        # Handle uploaded image
        image_data = None
        if uploaded_file is not None:
            # Read and encode image
            image_bytes = uploaded_file.read()
            image_data = base64.b64encode(image_bytes).decode('utf-8')
            # Increment upload key to reset the uploader for next message
            st.session_state.upload_key = upload_key + 1
        
        # Store message data in session state for processing
        st.session_state.pending_message = message_content
        if image_data:
            st.session_state.pending_image_data = image_data
        
        # Add user message to history immediately
        message_data = {"role": "user", "content": message_content}
        if image_data:
            message_data["image_data"] = image_data
        st.session_state.messages.append(message_data)
        
        # Set processing flag and rerun to show spinner
        st.session_state.processing = True
        st.rerun()

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