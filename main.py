"""
Main application for Talk-To-Anyone. Starter of ALL!
"""
import streamlit as st
from src.api import initialize_api
from src.utils import initialize_session_state, reset_chat_state
from src.ui import (
    render_chat_messages, 
    render_source_popover,
    render_persona_setup, 
    handle_chat_interaction,
    render_persona_room_setup, 
    handle_persona_room_interaction
)

st.title("Talk To Anyone 🗣️")

# starm em states
initialize_session_state()

# api startip
client, error_message = initialize_api()
if error_message:
    st.error(error_message)
    st.stop()

# show personas if dev
st.session_state.developer_mode = st.sidebar.toggle(
    "Developer Mode", value=st.session_state.developer_mode
)

current_chat_mode_selection = st.sidebar.radio(
    "Select Chat Mode:",
    ("Single Persona Chat", "Persona Room"),
    index=0 if st.session_state.chat_mode == "Single Persona Chat" else 1,
    key="chat_mode_selection_radio",
)

# reset on chat mode
if current_chat_mode_selection != st.session_state.chat_mode:
    st.session_state.chat_mode = current_chat_mode_selection
    reset_chat_state()
    st.rerun()

if not st.session_state.start_chat:
    if st.session_state.chat_mode == "Single Persona Chat":
        if render_persona_setup(client):
            st.rerun()
    elif st.session_state.chat_mode == "Persona Room":
        if render_persona_room_setup(client):
            st.rerun()
else:
    render_source_popover()
    render_chat_messages()
    
    if st.session_state.chat_mode == "Single Persona Chat":
        handle_chat_interaction(client)
    elif st.session_state.chat_mode == "Persona Room":
        handle_persona_room_interaction(client)
        
    if st.sidebar.button("⬅️ New Chat / Exit Room", key="exit_chat_btn"):
        reset_chat_state()
        st.rerun()
