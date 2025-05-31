"""
Voice settings UI components for Talk-To-Anyone application.
"""
import streamlit as st
import base64
from ..models.voice import VOICE_OPTIONS, generate_single_voice_audio, get_voice_style_suggestions

def render_voice_settings():
    """
    Render voice settings in the sidebar.
    """
    with st.sidebar.expander("🎵 Voice Settings", expanded=False):
        st.session_state.voice_enabled = st.toggle(
            "Enable Voice Personas", 
            value=st.session_state.voice_enabled,
            help="Generate audio for persona responses using TTS"
        )
        
        if st.session_state.voice_enabled:
            st.session_state.auto_play_voice = st.toggle(
                "Auto-play audio", 
                value=st.session_state.auto_play_voice,
                help="Automatically play audio when personas respond"
            )
            
            st.markdown("**Voice Preview:**")
            preview_text = "Hello! This is how I sound."
            preview_voice = st.selectbox(
                "Test a voice:",
                options=list(VOICE_OPTIONS.keys()),
                format_func=lambda x: f"{x} ({VOICE_OPTIONS[x]})",
                key="voice_preview_select"
            )
            
            if st.button("🔊 Play Preview", key="voice_preview_btn"):
                with st.spinner("Generating voice preview..."):
                    from ..api import initialize_api
                    client, _ = initialize_api()
                    if client:
                        audio_data = generate_single_voice_audio(
                            client, preview_text, preview_voice
                        )
                        if audio_data:
                            audio_b64 = base64.b64encode(audio_data).decode()
                            st.audio(f"data:audio/wav;base64,{audio_b64}")

def render_persona_voice_config(persona_num, persona_name, persona_description):
    """
    Render voice configuration for a specific persona.
    
    Args:
        persona_num (int): Persona number (1 or 2)
        persona_name (str): Name of the persona
        persona_description (str): Description of the persona
    """
    if not st.session_state.voice_enabled:
        return
    
    voice_key = f"persona_{persona_num}_voice"
    style_key = f"persona_{persona_num}_voice_style"
    
    st.markdown(f"**🎵 Voice for {persona_name}:**")
    
    # Auto-suggest voice based on description
    if persona_description and st.button(f"🎯 Auto-suggest voice for {persona_name}", key=f"suggest_voice_{persona_num}"):
        suggestion = get_voice_style_suggestions(persona_description)
        st.session_state[voice_key] = suggestion["voice"]
        st.session_state[style_key] = suggestion["style"]
        st.success(f"Suggested voice: {suggestion['voice']} with style: {suggestion['style']}")
    
    # Voice selection
    current_voice = getattr(st.session_state, voice_key, "Zephyr")
    selected_voice = st.selectbox(
        f"Voice for {persona_name}:",
        options=list(VOICE_OPTIONS.keys()),
        index=list(VOICE_OPTIONS.keys()).index(current_voice) if current_voice in VOICE_OPTIONS else 0,
        format_func=lambda x: f"{x} ({VOICE_OPTIONS[x]})",
        key=f"voice_select_{persona_num}"
    )
    setattr(st.session_state, voice_key, selected_voice)
    
    # Style prompt
    current_style = getattr(st.session_state, style_key, "")
    style_prompt = st.text_input(
        f"Speaking style for {persona_name}:",
        value=current_style,
        placeholder="e.g., 'Speak with wisdom and authority', 'Sound excited and youthful'",
        key=f"style_input_{persona_num}"
    )
    setattr(st.session_state, style_key, style_prompt)

def create_audio_player(audio_data, auto_play=False):
    """
    Create an audio player for the generated speech.
    
    Args:
        audio_data (bytes): Wave file data
        auto_play (bool): Whether to auto-play the audio
        
    Returns:
        str: HTML audio element
    """
    if not audio_data:
        return ""
    
    audio_b64 = base64.b64encode(audio_data).decode()
    autoplay_attr = "autoplay" if auto_play else ""
    
    return f"""
    <audio controls {autoplay_attr} style="width: 100%;">
        <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
        Your browser does not support the audio element.
    </audio>
    """
