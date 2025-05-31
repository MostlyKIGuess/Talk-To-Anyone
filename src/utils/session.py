"""
Session state utilities for Talk-To-Anyone application.
"""
import streamlit as st
import time
import base64

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

    # Voice settings
    if "voice_enabled" not in st.session_state:
        st.session_state.voice_enabled = False
    if "auto_play_voice" not in st.session_state:
        st.session_state.auto_play_voice = True

    # Persona 1
    if "persona_1_name" not in st.session_state:
        st.session_state.persona_1_name = ""
    if "persona_1_description" not in st.session_state:
        st.session_state.persona_1_description = None
    if "persona_1_session" not in st.session_state:
        st.session_state.persona_1_session = None
    if "persona_1_voice" not in st.session_state:
        st.session_state.persona_1_voice = "Zephyr"
    if "persona_1_voice_style" not in st.session_state:
        st.session_state.persona_1_voice_style = ""

    # Persona 2 (for Persona Room)
    if "persona_2_name" not in st.session_state:
        st.session_state.persona_2_name = ""
    if "persona_2_description" not in st.session_state:
        st.session_state.persona_2_description = None
    if "persona_2_session" not in st.session_state:
        st.session_state.persona_2_session = None
    if "persona_2_voice" not in st.session_state:
        st.session_state.persona_2_voice = "Puck"
    if "persona_2_voice_style" not in st.session_state:
        st.session_state.persona_2_voice_style = ""

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
    st.session_state.persona_1_voice = "Zephyr"
    st.session_state.persona_1_voice_style = ""
    st.session_state.persona_2_name = ""
    st.session_state.persona_2_description = None
    st.session_state.persona_2_session = None
    st.session_state.persona_2_voice = "Puck"
    st.session_state.persona_2_voice_style = ""
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
    # Convert messages with audio data to JSON-serializable format
    serializable_messages = []
    for msg in st.session_state.messages_display:
        serializable_msg = msg.copy()
        
        # Convert audio data to base64 string if present
        if "audio_data" in serializable_msg and serializable_msg["audio_data"]:
            if isinstance(serializable_msg["audio_data"], bytes):
                serializable_msg["audio_data"] = base64.b64encode(serializable_msg["audio_data"]).decode('utf-8')
        
        serializable_messages.append(serializable_msg)
    
    chat_data = {
        "timestamp": time.time(),
        "chat_mode": st.session_state.chat_mode,
        "messages": serializable_messages,
        "sources": st.session_state.all_sources,
        "voice_settings": {
            "voice_enabled": st.session_state.voice_enabled,
            "auto_play_voice": st.session_state.auto_play_voice
        },
        "persona_data": {}
    }
    
    # Add persona 1 data
    chat_data["persona_data"]["persona_1"] = {
        "name": st.session_state.persona_1_name,
        "description": st.session_state.persona_1_description,
        "voice": st.session_state.persona_1_voice,
        "voice_style": st.session_state.persona_1_voice_style
    }
    
    # person2 iff in Persona Room
    if st.session_state.chat_mode == "Persona Room":
        chat_data["persona_data"]["persona_2"] = {
            "name": st.session_state.persona_2_name,
            "description": st.session_state.persona_2_description,
            "voice": st.session_state.persona_2_voice,
            "voice_style": st.session_state.persona_2_voice_style
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
        
        # Convert messages with base64 audio data back to bytes
        imported_messages = []
        for msg in chat_data.get("messages", []):
            imported_msg = msg.copy()
            
            # Convert base64 string back to bytes if present
            if "audio_data" in imported_msg and imported_msg["audio_data"]:
                if isinstance(imported_msg["audio_data"], str):
                    try:
                        imported_msg["audio_data"] = base64.b64decode(imported_msg["audio_data"])
                    except Exception as e:
                        st.warning(f"Could not decode audio data for message: {e}")
                        imported_msg["audio_data"] = None
            
            imported_messages.append(imported_msg)
        
        # setup msg, sources
        st.session_state.messages_display = imported_messages
        st.session_state.all_sources = chat_data.get("sources", [])
        
        # voice settings
        voice_settings = chat_data.get("voice_settings", {})
        st.session_state.voice_enabled = voice_settings.get("voice_enabled", False)
        st.session_state.auto_play_voice = voice_settings.get("auto_play_voice", True)
        
        persona_data = chat_data.get("persona_data", {})
        
        # Persona 1
        persona_1 = persona_data.get("persona_1", {})
        st.session_state.persona_1_name = persona_1.get("name", "")
        st.session_state.persona_1_description = persona_1.get("description", None)
        st.session_state.persona_1_voice = persona_1.get("voice", "Zephyr")
        st.session_state.persona_1_voice_style = persona_1.get("voice_style", "")
        
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
            st.session_state.persona_2_voice = persona_2.get("voice", "Puck")
            st.session_state.persona_2_voice_style = persona_2.get("voice_style", "")
            
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
