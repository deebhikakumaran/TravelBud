import streamlit as st
import time
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="TravelBud",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

custom_css = """
<style>
    [data-testid="stAppViewContainer"] {
        background-color: #131314;
    }
    
    .stChatInputContainer {
        background-color: #2f2f2f !important;
        border-radius: 25px !important;
        border: 1px solid #4f4f4f !important;
    }
    
    .stChatInputContainer textarea {
        color: #e8eaed !important;
    }
    
    [data-testid="stChatMessage"] {
        padding: 1rem;
    }
    
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 70vh;
        text-align: center;
    }
    
    .welcome-title {
        color: #e8eaed;
        font-size: 48px;
        margin-bottom: 20px;
        background: linear-gradient(90deg, #4285f4, #ea4335, #fbbc04, #34a853);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .welcome-subtitle {
        color: #9aa0a6;
        font-size: 20px;
    }
    
    /* Hide Streamlit branding */
    footer {visibility: hidden;}
    .stChatFloatingInputContainer {bottom: 20px;}
</style>
"""

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "first_run" not in st.session_state:
        st.session_state.first_run = True

def display_welcome_screen():
    """Display the welcome screen when no messages exist"""
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-title">TravelBud</div>
        <div class="welcome-subtitle">How can I help you today?</div>
    </div>
    """, unsafe_allow_html=True)

def handle_user_input(prompt: str):
    """Handle user input and generate response"""
    if prompt:
        # 1. Display and save user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 2. Call your uAgent in AgentVerse and get the response
        agent_response = call_uagent_agentverse(prompt)
        
        # 3. Display and save agent response
        with st.chat_message("assistant"):
            st.markdown(agent_response)
        st.session_state.messages.append({"role": "assistant", "content": agent_response})

        # Update first_run state
        st.session_state.first_run = False

def call_uagent_agentverse(prompt: str):
    """Call the uAgent in AgentVerse and return the response"""

    endpoint = "http://127.0.0.1:8000/send-query" 
    payload = {
        "text": prompt
    }
    try:
        response = requests.post(endpoint, json=payload)
        if response.status_code == 200:
            # agent = requests.get("http://127.0.0.1:8010/rest/get")
            return response.json().get("text", "No response text found")
        else:
            return f"Error: Received status code {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Connection error: {str(e)}"

def main():
    # Apply custom CSS
    st.markdown(custom_css, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Display welcome screen on first run
    if st.session_state.first_run and not st.session_state.messages:
        display_welcome_screen()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input (always at bottom)
    if prompt := st.chat_input("Ask TravelBud...", key="chat_input"):
        handle_user_input(prompt)

if __name__ == "__main__":
    main()




