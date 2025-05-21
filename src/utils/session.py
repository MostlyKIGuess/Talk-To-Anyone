"""
Session state utilities for Talk-To-Anyone application.
"""
import streamlit as st
import time

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


def export_chat_state():
    """
    Export the current chat state to a JSON structure.
    
    Returns:
        dict: A dictionary with all chat data for export
    """
    chat_data = {
        "timestamp": time.time(),
        "chat_mode": st.session_state.chat_mode,
        "messages": st.session_state.messages_display,
        "sources": st.session_state.all_sources,
        "persona_data": {}
    }
    
    # Add persona 1 data
    chat_data["persona_data"]["persona_1"] = {
        "name": st.session_state.persona_1_name,
        "description": st.session_state.persona_1_description
    }
    
    # person2 iff in Persona Room
    if st.session_state.chat_mode == "Persona Room":
        chat_data["persona_data"]["persona_2"] = {
            "name": st.session_state.persona_2_name,
            "description": st.session_state.persona_2_description
        }
    
    return chat_data

def import_chat_state(chat_data, client):
    """
    Import a saved chat state and initialize necessary chat sessions.
    
    Args:
        chat_data (dict): The saved chat data to import
        client: The Gemini API client
        
    Returns:
        bool: True if import was successful, False otherwise
    """
    from ..models import initialize_chat_session
    
    try:
        # what was the chat mode
        st.session_state.chat_mode = chat_data.get("chat_mode", "Single Persona Chat")
        
        # setup msg, sources
        st.session_state.messages_display = chat_data.get("messages", [])
        st.session_state.all_sources = chat_data.get("sources", [])
        
        persona_data = chat_data.get("persona_data", {})
        
        # Persona 1
        persona_1 = persona_data.get("persona_1", {})
        st.session_state.persona_1_name = persona_1.get("name", "")
        st.session_state.persona_1_description = persona_1.get("description", None)
        
        # now init the person 1 and 2 iff in Persona Room
        if st.session_state.persona_1_description:
            st.session_state.persona_1_session = initialize_chat_session(
                client, st.session_state.persona_1_description
            )
            if not st.session_state.persona_1_session:
                return False
        
        if st.session_state.chat_mode == "Persona Room":
            persona_2 = persona_data.get("persona_2", {})
            st.session_state.persona_2_name = persona_2.get("name", "")
            st.session_state.persona_2_description = persona_2.get("description", None)
            
            if st.session_state.persona_2_description:
                st.session_state.persona_2_session = initialize_chat_session(
                    client, st.session_state.persona_2_description
                )
                if not st.session_state.persona_2_session:
                    return False
        
        if st.session_state.chat_mode == "Persona Room":
            if st.session_state.messages_display:
                last_msg = st.session_state.messages_display[-1]
                st.session_state.last_actor = last_msg["role"]
                st.session_state.last_message_text = last_msg["text"]
                st.session_state.action_buttons_visible = True
            else:
                st.session_state.last_actor = None
                st.session_state.last_message_text = None
                st.session_state.action_buttons_visible = False
        
        st.session_state.start_chat = True
        
        return True
        
    except Exception as e:
        st.error(f"Error importing chat: {e}")
        return False
