import streamlit as st
from openai import AzureOpenAI
from config.settings import Config

@st.cache_resource(show_spinner=False)
def get_azure_openai_client():
    """Create and cache the Azure OpenAI client."""
    return AzureOpenAI(
        azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
        api_key=Config.AZURE_OPENAI_API_KEY,
        api_version=Config.AZURE_OPENAI_API_VERSION,
    )