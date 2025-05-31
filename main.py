"""
Main application for Talk-To-Anyone. Starter of ALL!
"""
import streamlit as st
import json
import base64
from src.api import initialize_api
from src.utils import initialize_session_state, reset_chat_state, export_chat_state, import_chat_state
from src.ui import (
    render_chat_messages, 
    render_source_popover,
    render_persona_setup, 
    handle_chat_interaction,
    render_persona_room_setup, 
    handle_persona_room_interaction,
    render_voice_settings
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

# Voice settings
render_voice_settings()

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

# import/export 
with st.sidebar.expander("Import/Export Chat", expanded=False):
    if st.session_state.start_chat and st.session_state.messages_display:
        export_data = export_chat_state()
        export_json = json.dumps(export_data)
        b64_export = base64.b64encode(export_json.encode()).decode()
        export_filename = f"talk_to_anyone_chat_{st.session_state.chat_mode.replace(' ', '_').lower()}.json"
        
        download_button_str = f'<a href="data:file/json;base64,{b64_export}" download="{export_filename}" style="display:inline-block;padding:0.25em 0.5em;text-decoration:none;background-color:#4CAF50;color:white;border-radius:4px;cursor:pointer;text-align:center;width:100%;"> Download Chat</a>'
        st.markdown(download_button_str, unsafe_allow_html=True)
    
    st.write("Import a saved chat:")
    uploaded_file = st.file_uploader("Choose a JSON file", type="json", key="chat_import_uploader")
    
    if uploaded_file is not None:
        try:
            import_data = json.load(uploaded_file)
            if st.button("Import Selected Chat", key="import_chat_btn"):
                with st.spinner("Importing chat and initializing personas..."):
                    if import_chat_state(import_data, client):
                        st.success("Chat imported successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to import chat. Please try again.")
        except Exception as e:
            st.error(f"Error reading the uploaded file: {e}")

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
