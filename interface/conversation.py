import json
import time
import streamlit as st
from services.azure_client import get_azure_openai_client
from services.assistant import ensure_assistant_and_thread
from tools.registry import TOOL_REGISTRY
from config.settings import Config


def validate_assistant_setup() -> str | None:
    """Validate that assistant and thread are properly set up.
    
    Returns:
        Error message if validation fails, None if successful.
    """
    ensure_assistant_and_thread()
    if "assistant_error" in st.session_state:
        return f"Assistant setup failed: {st.session_state.assistant_error}"
    if "assistant_id" not in st.session_state or "thread_id" not in st.session_state:
        return "Assistant not ready. Check your Azure keys and deployment name."
    return None


def create_user_message(client, user_message: str, image_data: str = None) -> None:
    """Create a user message in the thread."""
    content = []
    
    # Add text content
    content.append({"type": "text", "text": user_message})
    
    # If image data is provided, store it in session state for tools to access
    if image_data:
        st.session_state.uploaded_image_data = image_data
        # Don't append technical instructions - assistant's system prompt handles this automatically
    
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=content,
    )


def start_assistant_run(client):
    """Start a new assistant run and return the run object."""
    return client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=st.session_state.assistant_id,
    )


def extract_assistant_response(client) -> str:
    """Extract the assistant's response from the latest messages.
    
    Returns:
        The assistant's response text or a default message.
    """
    messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    ).data
    last_response = next((m for m in messages if m.role == "assistant"), None)
    if last_response:
        try:
            content = last_response.content[0].text.value
            return content if content.strip() else "Task completed successfully."
        except Exception:
            return "Response received but could not extract text content."
    return "No response received from assistant."


def handle_tool_calls(client, run_status, run):
    """Handle required tool calls and submit outputs.
    
    Args:
        client: Azure OpenAI client
        run_status: Current run status object
        run: The run object
    """
    ra = run_status.required_action.submit_tool_outputs.model_dump()
    tool_outputs = []
    
    for action in ra.get("tool_calls", []):
        func_name = action["function"]["name"]
        arguments = json.loads(action["function"]["arguments"])
        
        # Use the tool registry to call the appropriate function
        if func_name in TOOL_REGISTRY:
            output = TOOL_REGISTRY[func_name](**arguments)
            
            # Special handling for crop_image tool
            if func_name == "crop_image":
                try:
                    crop_result = json.loads(output)
                    if "cropped_image_b64" in crop_result:
                        # Store the cropped image in session state for display
                        st.session_state.cropped_image_data = crop_result
                        # Modify the output to be more user-friendly
                        output = json.dumps({
                            "success": True,
                            "message": f"Image cropped successfully to {crop_result['cropped_size']['width']}x{crop_result['cropped_size']['height']} pixels"
                        })
                except:
                    pass  # If parsing fails, use original output
            
            # Special handling for upscale_image tool
            if func_name == "upscale_image":
                try:
                    upscale_result = json.loads(output)
                    if "upscaled_image_b64" in upscale_result:
                        # Store the upscaled image in session state for display
                        st.session_state.upscaled_image_data = upscale_result
                        # Modify the output to be more user-friendly
                        scale = upscale_result.get('scale_factor', 'unknown')
                        new_size = upscale_result.get('upscaled_size', {})
                        width = new_size.get('width', 'unknown')
                        height = new_size.get('height', 'unknown')
                        output = json.dumps({
                            "success": True,
                            "message": f"Image upscaled {scale}x successfully to {width}x{height} pixels using OpenCV EDSR model"
                        })
                except:
                    pass  # If parsing fails, use original output
        else:
            output = json.dumps({"error": f"Unknown function: {func_name}"})
        
        tool_outputs.append({"tool_call_id": action["id"], "output": output})

    client.beta.threads.runs.submit_tool_outputs(
        thread_id=st.session_state.thread_id,
        run_id=run.id,
        tool_outputs=tool_outputs,
    )


def poll_run_completion(client, run, poll_interval_sec: float, max_wait_sec: int) -> str:
    """Poll for run completion and handle different statuses.
    
    Args:
        client: Azure OpenAI client
        run: The run object to poll
        poll_interval_sec: Time between polls
        max_wait_sec: Maximum time to wait
        
    Returns:
        Assistant response or error message
    """
    start = time.time()

    while True:
        if time.time() - start > max_wait_sec:
            return "Timed out waiting for the assistant. Please try again."

        time.sleep(poll_interval_sec)
        run_status = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id,
        )
        status = getattr(run_status, "status", None)

        if status == "completed":
            return extract_assistant_response(client)

        elif status == "requires_action":
            handle_tool_calls(client, run_status, run)

        elif status in {"failed", "cancelled", "expired"}:
            err = getattr(run_status, "last_error", None)
            return f"Run {status}. {err if err else ''}"

        # Continue polling for other statuses


def run_conversation(user_message: str, image_data: str = None, poll_interval_sec: float = None, max_wait_sec: int = None) -> dict:
    """Run a conversation with the assistant and return the response.
    
    Returns:
        dict with "content" key and optionally "cropped_image_data" or "upscaled_image_data" keys
    """
    # Use config defaults if not provided
    if poll_interval_sec is None:
        poll_interval_sec = Config.POLL_INTERVAL_SEC
    if max_wait_sec is None:
        max_wait_sec = Config.MAX_WAIT_SEC
    
    client = get_azure_openai_client()
    
    # Validate assistant setup
    error = validate_assistant_setup()
    if error:
        return {"content": error}

    # Create user message and start run
    create_user_message(client, user_message, image_data)
    run = start_assistant_run(client)

    # Poll for completion and return result
    content = poll_run_completion(client, run, poll_interval_sec, max_wait_sec)
    
    # Check if there's cropped or upscaled image data from the tool calls
    result = {"content": content}
    if "cropped_image_data" in st.session_state:
        result["cropped_image_data"] = st.session_state.cropped_image_data
        del st.session_state.cropped_image_data  # Clean up
    
    if "upscaled_image_data" in st.session_state:
        result["upscaled_image_data"] = st.session_state.upscaled_image_data
        del st.session_state.upscaled_image_data  # Clean up
    
    return result