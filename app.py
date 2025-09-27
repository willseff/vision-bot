import os
import json
import time
import requests
import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI

# =============================
# 🔧 Setup
# =============================
# Expect a file named azureopenai.env with:
#   AZURE_OPENAI_ENDPOINT=...
#   AZURE_OPENAI_API_KEY=...
#   OPENWEATHERMAP_API_KEY=...
load_dotenv("azureopenai.env")

# Create the Azure OpenAI client once per session
@st.cache_resource(show_spinner=False)
def get_oai_client():
    return AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-05-01-preview",
    )

client = get_oai_client()

# =============================
# 🌤️ Tool: get_weather (same logic as your CLI script)
# =============================

def get_weather(latitude, longitude):
    """Get the weather condition for a given location using latitude and longitude."""
    if latitude is None:
        return json.dumps({"weatherAPI_response": "Required argument latitude is not provided?"})
    if longitude is None:
        return json.dumps({"weatherAPI_response": "Required argument longitude is not provided?"})
    if latitude > 90 or latitude < -90:
        return json.dumps({"weatherAPI_response": "Invalid latitude value"})
    if longitude > 180 or longitude < -180:
        return json.dumps({"weatherAPI_response": "Invalid longitude value"})

    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    base_url = "https://api.openweathermap.org/data/3.0/onecall?"
    complete_url = f"{base_url}lat={latitude}&lon={longitude}&appid={api_key}&units=metric"

    response = requests.get(complete_url)
    response.raise_for_status()
    weather_data = response.json()

    weather_condition = weather_data["current"]["weather"][0]["description"]
    temperature = weather_data["current"]["temp"]

    return json.dumps({
        "latitude": latitude,
        "longitude": longitude,
        "weather_condition": weather_condition,
        "temperature": temperature
    })

# Define the tool schema for the Assistant API
TOOLS_LIST = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": (
            "Get the weather condition using latitude and longitude. "
            "If any argument is missing in the user message, assume it as 'null' and not zero (0) or don't return missing argument value yourself"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number", "description": "Latitude of the location"},
                "longitude": {"type": "number", "description": "Longitude of the location"},
            },
            "required": ["latitude", "longitude"],
        },
    },
}]

# =============================
# 🧠 Lazy init: Assistant & Thread (create only when needed)
# =============================

def ensure_assistant_and_thread():
    """Create assistant/thread only when first needed to avoid blank page on load."""
    if "assistant_id" not in st.session_state:
        try:
            with st.spinner("Setting up assistant..."):
                assistant = client.beta.assistants.create(
                    name="Weather Assistant",
                    instructions=(
                        "You are a weather assistant that provides weather information using real-time data. "
                        "When the user provides a location, call get_weather with latitude and longitude."
                    ),
                    tools=TOOLS_LIST,
                    model="gpt-4.1-mini",  # <-- replace with your Azure OpenAI deployment name
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

# =============================
# 🚀 Core run function adapted for Streamlit
#   - returns the assistant's text
#   - no prints / blocking input loop
# =============================

def run_conversation(user_message: str, poll_interval_sec: float = 1.5, max_wait_sec: int = 90) -> str:
    # Ensure assistant/thread exist (lazy)
    ensure_assistant_and_thread()
    if "assistant_error" in st.session_state:
        return f"❌ Assistant setup failed: {st.session_state.assistant_error}"
    if "assistant_id" not in st.session_state or "thread_id" not in st.session_state:
        return "❌ Assistant not ready. Check your Azure keys and deployment name."

    # Create user message
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_message,
    )

    # Kick off a run
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=st.session_state.assistant_id,
    )

    # Poll for completion, handling tool calls
    start = time.time()
    assistant_message_content = None

    while True:
        if time.time() - start > max_wait_sec:
            return "⚠️ Timed out waiting for the assistant. Please try again."

        time.sleep(poll_interval_sec)
        run_status = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id,
        )
        status = getattr(run_status, "status", None)

        if status == "completed":
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            ).data
            last_response = next((m for m in messages if m.role == "assistant"), None)
            if last_response:
                try:
                    assistant_message_content = last_response.content[0].text.value
                except Exception:
                    assistant_message_content = "(No text content returned)"
            break

        elif status == "requires_action":
            ra = run_status.required_action.submit_tool_outputs.model_dump()
            tool_outputs = []
            for action in ra.get("tool_calls", []):
                func_name = action["function"]["name"]
                arguments = json.loads(action["function"]["arguments"])
                if func_name == "get_weather":
                    output = get_weather(
                        latitude=arguments.get("latitude"),
                        longitude=arguments.get("longitude"),
                    )
                else:
                    output = json.dumps({"error": f"Unknown function: {func_name}"})
                tool_outputs.append({"tool_call_id": action["id"], "output": output})

            client.beta.threads.runs.submit_tool_outputs(
                thread_id=st.session_state.thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs,
            )

        elif status in {"failed", "cancelled", "expired"}:
            err = getattr(run_status, "last_error", None)
            return f"❌ Run {status}. {err if err else ''}"

        else:
            continue

    return assistant_message_content or "(No function calls were made by the model.)"

# =============================
# 💬 Streamlit Chat UI
# =============================

st.set_page_config(page_title="Weather Assistant", page_icon="🌤️")
st.title("Weather Assistant 🌤️")

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

# Sidebar: quick tips
with st.sidebar:
    st.header("Setup")
    st.markdown("""
    **1. Install deps**
    ```bash
    pip install streamlit python-dotenv "openai>=1.40" requests
    ```
    **2. Run locally**
    ```bash
    streamlit run streamlit_app.py
    ```
    **Troubleshooting**
    - Ensure `azureopenai.env` is in the same folder and contains valid keys.
    - Replace `model` with your **Azure deployment name** (e.g., `gpt-4o-mini`).
    - If the page is blank, check your terminal for errors and try: `streamlit run streamlit_app.py --server.runOnSave=false`.
    - The assistant and thread are created lazily on first message, so the page should render even if keys are missing.
    """)
