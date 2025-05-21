"""
Session state utilities for Talk-To-Anyone application.
"""
import streamlit as st

def initialize_session_state():
    """
    Initialize all the necessary session state variables.
    """
    # Main states
    if "start_chat" not in st.session_state:
        st.session_state.start_chat = False
    if "messages_display" not in st.session_state:
        st.session_state.messages_display = []
    if "developer_mode" not in st.session_state:
        st.session_state.developer_mode = False
    if "chat_mode" not in st.session_state:
        st.session_state.chat_mode = "Single Persona Chat"
    if "all_sources" not in st.session_state:
        st.session_state.all_sources = []

    # Persona 1
    if "persona_1_name" not in st.session_state:
        st.session_state.persona_1_name = ""
    if "persona_1_description" not in st.session_state:
        st.session_state.persona_1_description = None
    if "persona_1_session" not in st.session_state:
        st.session_state.persona_1_session = None

    # Persona 2 (for Persona Room)
    if "persona_2_name" not in st.session_state:
        st.session_state.persona_2_name = ""
    if "persona_2_description" not in st.session_state:
        st.session_state.persona_2_description = None
    if "persona_2_session" not in st.session_state:
        st.session_state.persona_2_session = None

    # Room relevant states 
    if "action_buttons_visible" not in st.session_state:
        st.session_state.action_buttons_visible = False
    if "last_actor" not in st.session_state:  # "User", persona_1_name, persona_2_name
        st.session_state.last_actor = None
    if "last_message_text" not in st.session_state:  # Text of the last message for context
        st.session_state.last_message_text = None

def reset_chat_state():
    """
    Reset the chat state variables when starting a new chat.
    """
    st.session_state.start_chat = False
    st.session_state.messages_display = []
    st.session_state.persona_1_name = ""
    st.session_state.persona_1_description = None
    st.session_state.persona_1_session = None
    st.session_state.persona_2_name = ""
    st.session_state.persona_2_description = None
    st.session_state.persona_2_session = None
    st.session_state.action_buttons_visible = False
    st.session_state.last_actor = None
    st.session_state.last_message_text = None
    st.session_state.all_sources = []
