"""
Single Persona Chat UI components for Talk-To-Anyone application.
"""
import streamlit as st
from ..models import (
    generate_persona_description_from_name, 
    initialize_chat_session, 
    extract_sources_from_response,
    generate_single_voice_audio
)
from .voice_settings import render_persona_voice_config, create_audio_player

def render_persona_setup(client):
    """
    Render the UI for setting up a single persona chat.
    
    Args:
        client: The Gemini API client
        
    Returns:
        bool: True if chat should start, False otherwise
    """
    st.subheader("Who do you want to talk to?")
    p1_name_input = st.text_input(
        "E.g., Albert Einstein, a futuristic AI assistant, a pirate captain",
        value=st.session_state.persona_1_name,
        key="persona_1_name_text_input",
    )
    st.session_state.persona_1_name = p1_name_input

    if st.button(
        "✨ Generate Persona",
        disabled=not st.session_state.persona_1_name,
        key="generate_single_persona_btn",
    ):
        with st.spinner(
            f"Generating persona description for {st.session_state.persona_1_name}..."
        ):
            st.session_state.persona_1_description = generate_persona_description_from_name(
                client, st.session_state.persona_1_name
            )

    if st.session_state.persona_1_description:
        if st.session_state.developer_mode:
            st.subheader("Generated Persona Description (System Prompt):")
            st.markdown(st.session_state.persona_1_description)

        # Voice configuration
        render_persona_voice_config(1, st.session_state.persona_1_name, st.session_state.persona_1_description)

        if st.button(
            f"👍 Yes, I want to talk to {st.session_state.persona_1_name}!",
            key="confirm_single_persona_btn",
        ):
            st.session_state.persona_1_session = initialize_chat_session(
                client, st.session_state.persona_1_description
            )
            if st.session_state.persona_1_session:
                st.session_state.start_chat = True
                st.session_state.messages_display = []
                st.session_state.all_sources = []
                return True
            else:
                st.error("Failed to initialize chat session for persona.")
    
    return False


def handle_chat_interaction(client):
    """
    Handle the chat interaction for single persona chat.
    
    Args:
        client: The Gemini API client
    """
    if st.session_state.persona_1_session and st.session_state.persona_1_name:
        user_prompt = st.chat_input(
            f"Talk to {st.session_state.persona_1_name}...", key="single_chat_input"
        )

        if user_prompt:
            st.session_state.messages_display.append(
                {"role": "User", "text": user_prompt, "sources": []}
            )
            with st.chat_message("User"):
                st.markdown(user_prompt)

            with st.spinner(f"{st.session_state.persona_1_name} is thinking..."):
                try:
                    response = st.session_state.persona_1_session.send_message(
                        user_prompt
                    )
                    if response is None:
                        st.error("Received no response from Gemini.")
                        if (
                            st.session_state.messages_display
                            and st.session_state.messages_display[-1]["role"]
                            == "User"
                        ):
                            st.session_state.messages_display.pop()
                        st.rerun()
                    else:
                        model_response_text = (
                            response.text
                            if hasattr(response, "text")
                            and response.text is not None
                            else "No text in response."
                        )
                        sources = extract_sources_from_response(response)
                        
                        existing_uris = {s['uri'] for s in st.session_state.all_sources if 'uri' in s}
                        for src in sources:
                            if src.get('uri') and src['uri'] not in existing_uris:
                                st.session_state.all_sources.append(src)
                                existing_uris.add(src['uri'])
                        
                        # Generate voice audio if enabled
                        audio_data = None
                        if st.session_state.voice_enabled and model_response_text != "No text in response.":
                            with st.spinner("Generating voice..."):
                                audio_data = generate_single_voice_audio(
                                    client,
                                    model_response_text,
                                    st.session_state.persona_1_voice,
                                    st.session_state.persona_1_voice_style
                                )
                                
                        message = {
                            "role": st.session_state.persona_1_name,
                            "text": model_response_text,
                            "sources": sources,
                            "audio_data": audio_data
                        }
                        st.session_state.messages_display.append(message)
                        st.rerun()
                except Exception as e:
                    st.error(f"Error getting response from Gemini: {e}")
                    if (
                        st.session_state.messages_display
                        and st.session_state.messages_display[-1]["role"] == "User"
                    ):
                        st.session_state.messages_display.pop()
    else:
        st.warning(
            "Chat session or persona name is missing for Single Persona Chat."
        )
        st.session_state.start_chat = False
        st.rerun()
