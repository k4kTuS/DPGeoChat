import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AnyMessage, AIMessage
import streamlit as st

load_dotenv()

# LLM options are visible in the UI
LLM_OPTIONS = ['gpt-4o-mini', 'gpt-4o', 'gemini-2.0-flash', 'llama-3.1-8b-instant']
# All utilized LLMs
LLM_PROVIDERS = {
    'gpt-4o-mini': 'openai',
    'gpt-4o': 'openai',
    'llama-3.1-8b-instant': 'groq',
    'mistral-small3.1:24b-instruct-2503-fp16': 'ollama',
    'qwen2.5:32b-instruct-fp16': 'ollama',
    'qwen2.5:7b-instruct-fp16': 'ollama',
    'llama3.2:3b-instruct-fp16': 'ollama',
    'llama3.1:8b-instruct-fp16': 'ollama',
    'gemini-2.0-flash': 'google',
    'gemini-2.0-flash-lite': 'google',
}
DEFAULT_LLM = 'gpt-4o-mini'

def get_chat_history(alternative: bool = False) -> InMemoryChatMessageHistory:
    """
    Returns the chat history for the current thread. If the thread is not found, it creates a new one."""
    chat_key = f'chat_{st.session_state.thread_id}' if not alternative else f'chat_alt_{st.session_state.thread_id}'
    if chat_key not in st.session_state:
        st.session_state[chat_key] = InMemoryChatMessageHistory()
    return st.session_state[chat_key]

def clear_chat_history():
    """
    Clears the chat history for the current thread. This is used when a new thread is created.
    """
    chat_key = f'chat_{st.session_state.thread_id}'
    chat_alt_key = f'chat_alt_{st.session_state.thread_id}'
    if chat_key in st.session_state:
        del st.session_state[chat_key]
    if chat_alt_key in st.session_state:
        del st.session_state[chat_alt_key]
    st.session_state.all_messages = {}

def get_llm(model_name: str) -> BaseChatModel:
    """
    Returns the LLM model based on project configuration. Currently supports OpenAI, Ollama, Groq and GoogleAI Studio.
    """
    provider = LLM_PROVIDERS.get(model_name, None)
    if provider == 'openai':
        return ChatOpenAI(
                    model=model_name,
                    temperature=0,
                    max_retries=2,
                )
    if provider == 'ollama':
        return ChatOllama(
                    model=model_name,
                    temperature=0,
                    max_retries=2,
                    base_url=os.getenv('OLLAMA_API_URL', 'http://localhost:11434'),
                )
    if provider == 'groq':
        return ChatGroq(
                    model=model_name,
                    temperature=0,
                    max_retries=2,
                )
    if provider == 'google':
        return ChatGoogleGenerativeAI(
                    model=model_name,
                    temperature=0,
                    max_retries=0,
                )
    raise ValueError(f"Unknown LLM provider for model: {model_name}")

def store_run_messages(messages: list[AnyMessage], alternative: bool = False):
    """
    Add all messages to the chat history and store each message in the session state.
    """
    get_chat_history(alternative=alternative).add_messages(messages)
    for message in messages:
        st.session_state.all_messages[message.id] = message

def pair_response_messages(run_id: str, main: AIMessage, alternative: AIMessage):
    """
    Set the metadata for the main and alternative messages to link them together.
    """
    main.alternative_id = alternative.id
    alternative.alternative_id = main.id
    alternative.run_id = run_id