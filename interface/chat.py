import streamlit as st
import streamlit.components.v1 as components
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
    for i, msg in enumerate(st.session_state.messages):
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
                st.download_button(
                    "Download Cropped Image",
                    data=base64.b64decode(crop_data['cropped_image_b64']),
                    file_name="cropped_image.jpg",
                    mime="image/jpeg",
                    key=f"download_cropped_{i}"
                )
            
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
                st.download_button(
                    "Download Upscaled Image",
                    data=base64.b64decode(upscale_data['upscaled_image_b64']),
                    file_name="upscaled_image.png",
                    mime="image/png",
                    key=f"download_upscaled_{i}"
                )

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

def render_architecture_page():
    """Render the architecture/how it was built page."""
    st.title("How Vision Bot Was Built")
    
    st.markdown("""
    ## Architecture Overview
    
    Vision Bot is a Streamlit-based AI assistant that combines multiple Azure AI services to provide intelligent image processing and conversational capabilities.
    
    ### Key Components
    
    **Frontend (Streamlit)**
    - Interactive chat interface
    - Image upload and display
    - Real-time conversation with AI assistant
    
    **Backend Services**
    - **Azure OpenAI**: Powers the conversational AI assistant
    - **Azure Vision Studio**: Provides computer vision capabilities for smart cropping
    - **OpenWeatherMap API**: Supplies weather information
    - **OpenCV**: Upscaling using EDSR models

    **Architecture Flow (Scroll right to view entire image)**
    """)
    
    # Display the flowchart SVG
    try:
        with open("test_images/Vision Bot.drawio.svg", "r") as f:
            svg_content = f.read()
        st.components.v1.html(svg_content, height=520, width=1400, scrolling=True)
    except FileNotFoundError:
        st.error("Architecture diagram not found. Please ensure 'Vision Bot.drawio.svg' exists in the test_images directory.")
    except Exception as e:
        st.error(f"Error loading diagram: {e}")
    
    st.markdown("""
    ### Technology Stack
    
    - **Python 3.11+**
    - **Streamlit** - Web framework
    - **Azure OpenAI** - AI assistant
    - **Azure Vision Studio** - Smart Cropping
    - **OpenCV** - Image processing
    - **Pillow** - Image manipulation
    - **aiohttp** - Async HTTP client for concurrent requests
    
    ### Scalability & Performance
    
    **Handling Large Numbers of Concurrent Users**
    
    Vision Bot is designed to scale efficiently and handle high traffic loads:
    
    - **Azure Container Apps with KEDA**: The application is containerized and deployed on Azure Container Apps, which automatically scales based on demand using Kubernetes Event-driven Autoscaling (KEDA). This ensures the app can handle sudden spikes in traffic by scaling out additional container instances.

    - **Azure Computer Vision**: Smart cropping uses Azure's scalable Computer Vision service, which processes images concurrently.

    - **Async API Architecture**: The backend uses asynchronous APIs throughout:
      - **aiohttp** for non-blocking HTTP requests to external services
      - **Async Azure SDK calls** for Computer Vision and OpenAI operations
      - **Concurrent processing** of multiple user requests without blocking
      - **Efficient resource utilization** through async/await patterns
    
    - **Load Balancing**: Azure Container Apps automatically distributes traffic across scaled instances
    - **Auto-scaling triggers**: Based on CPU usage, memory, and custom metrics
    
    ### Key Features Implemented
    
    - **Conversational AI**: Natural language processing with context awareness
    - **Smart Image Cropping**: AI-powered content detection and cropping
    - **Image Upscaling**: Super-resolution using OpenCV EDSR models
    - **Weather Integration**: Real-time weather data from OpenWeatherMap
    - **Async Processing**: Non-blocking operations for concurrent user handling
    """)
    
    st.markdown("""
    ### Source Code & Related Projects
    
    **GitHub Repositories:**
    
    - **[Vision Bot](https://github.com/willseff/vision-bot)** - This Streamlit-based AI assistant
    - **[OpenCV Upscale App](https://github.com/willseff/opencv-upscale-app)** - Standalone image upscaling application using OpenCV EDSR models
    
    """)

def render_sidebar():
    """Render the sidebar with a summary of app capabilities."""
    with st.sidebar:
        st.header("What you can do")
        
        # Prepare test image links
        test_image_links = {}
        with open("test_images/presentation.png", "rb") as f:
            b64_data = base64.b64encode(f.read()).decode()
            test_image_links["presentation"] = f'data:image/png;base64,{b64_data}'
        
        with open("test_images/low_res.jpg", "rb") as f:
            b64_data = base64.b64encode(f.read()).decode()
            test_image_links["low_res"] = f'data:image/jpeg;base64,{b64_data}'
        
        st.markdown(f"""
        **Chat with AI Assistant**
        - Ask questions and get intelligent responses powered by Azure OpenAI
        
        **Get Weather Information**
        - Try asking: "What's the weather like in New York?"
        
        **Smart Crop Images**
        - Upload an image and ask the assistant to crop it intelligently
        - Example: Upload [{"presentation.png"}] and ask "Crop this presentation slide to focus on the main content"
        - The cropped image will be displayed and you can download it
        
        **Upscale Images**
        - Upload a low-resolution image and ask to upscale it using AI
        - Example: Upload [{"low_res.jpg"}] and ask "Upscale this image"
        - The upscaled image will be displayed and you can download it
        """.replace("[", "<a href='" + test_image_links.get("presentation", "#") + "' download='presentation.png'>").replace("]", "</a>").replace("{{", "<a href='" + test_image_links.get("low_res", "#") + "' download='low_res.jpg'>").replace("}}", "</a>"), unsafe_allow_html=True)
        
