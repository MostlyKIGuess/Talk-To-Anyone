"""
Voice settings UI components for Talk-To-Anyone application.
"""
import streamlit as st
import base64
from ..models.voice import (
    VOICE_OPTIONS, SUPPORTED_LANGUAGES, get_voices_by_gender,
    generate_single_voice_audio, get_voice_style_suggestions
)

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
            
            default_lang = "English (US)"
            if "preferred_language" not in st.session_state:
                st.session_state.preferred_language = default_lang
                
            st.session_state.preferred_language = st.selectbox(
                "Preferred Language:",
                options=list(SUPPORTED_LANGUAGES.keys()),
                index=list(SUPPORTED_LANGUAGES.keys()).index(st.session_state.preferred_language) 
                      if st.session_state.preferred_language in SUPPORTED_LANGUAGES else 0,
                help="Language for voice generation (auto-detected if not specified)"
            )
            
            st.markdown("**Voice Preview:**")
            
            gender_filter = st.selectbox(
                "Filter by gender:",
                options=["All", "Male", "Female", "Neutral"],
                key="voice_preview_gender_filter"
            )
            
            filter_map = {"All": None, "Male": "male", "Female": "female", "Neutral": "neutral"}
            filtered_voices = get_voices_by_gender(filter_map[gender_filter])
            
            preview_voice = st.selectbox(
                "Test a voice:",
                options=list(filtered_voices.keys()),
                format_func=lambda x: f"{x} ({filtered_voices[x]['style']}) - {filtered_voices[x]['gender'].title()}",
                key="voice_preview_select"
            )
            
            preview_text = st.text_input(
                "Preview text:",
                value="Hello! This is how I sound.",
                key="voice_preview_text"
            )
            
            if st.button("🔊 Play Preview", key="voice_preview_btn"):
                with st.spinner("Generating voice preview..."):
                    from ..api import initialize_api
                    client, _ = initialize_api()
                    if client:
                        language_hint = st.session_state.preferred_language if st.session_state.preferred_language != "English (US)" else ""
                        audio_data = generate_single_voice_audio(
                            client, preview_text, preview_voice, language_hint=language_hint
                        )
                        if audio_data:
                            audio_b64 = base64.b64encode(audio_data).decode()
                            st.audio(f"data:audio/wav;base64,{audio_b64}")

def render_persona_voice_config(persona_num, persona_name, persona_description):
    """
    Render voice configuration for a specific persona with enhanced suggestions.
    
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
    if persona_description and st.button(f"🎯 Smart Voice Suggestion for {persona_name}", key=f"suggest_voice_{persona_num}"):
        suggestion = get_voice_style_suggestions(persona_description)
        st.session_state[voice_key] = suggestion["voice"]
        st.session_state[style_key] = suggestion["style"]
        
        # Show detailed suggestion info
        st.success(f"✨ **Suggested:** {suggestion['voice']} ({VOICE_OPTIONS[suggestion['voice']]['style']})")
        st.info(f"**Reason:** {suggestion['reason']} (Detected: {suggestion['gender']})")
        
        # Show alternatives
        if suggestion.get('alternatives'):
            with st.expander("🔄 Alternative Suggestions"):
                for i, alt in enumerate(suggestion['alternatives']):
                    if st.button(f"{alt['voice']} - {alt['reason']}", key=f"alt_voice_{persona_num}_{i}"):
                        st.session_state[voice_key] = alt["voice"]
                        st.session_state[style_key] = alt["style"]
                        st.rerun()
    
    # Gender-based voice filtering
    detected_gender = "neutral"
    if persona_description:
        from ..models.voice import detect_persona_gender
        detected_gender = detect_persona_gender(persona_description)
    
    gender_filter = st.selectbox(
        f"Voice gender for {persona_name}:",
        options=["Auto-detect", "Male", "Female", "All"],
        index=0,
        key=f"gender_filter_{persona_num}",
        help=f"Auto-detected: {detected_gender.title()}"
    )
    
    # Get filtered voices
    if gender_filter == "Auto-detect":
        available_voices = get_voices_by_gender(detected_gender)
    elif gender_filter == "All":
        available_voices = VOICE_OPTIONS
    else:
        available_voices = get_voices_by_gender(gender_filter.lower())
    
    # Voice selection
    current_voice = getattr(st.session_state, voice_key, "Zephyr")
    if current_voice not in available_voices:
        current_voice = list(available_voices.keys())[0] if available_voices else "Zephyr"
        
    selected_voice = st.selectbox(
        f"Voice for {persona_name}:",
        options=list(available_voices.keys()),
        index=list(available_voices.keys()).index(current_voice) if current_voice in available_voices else 0,
        format_func=lambda x: f"{x} ({available_voices[x]['style']}) - {available_voices[x]['personality']}",
        key=f"voice_select_{persona_num}"
    )
    setattr(st.session_state, voice_key, selected_voice)
    
    # Style prompt
    current_style = getattr(st.session_state, style_key, "")
    style_prompt = st.text_area(
        f"Speaking style for {persona_name}:",
        value=current_style,
        placeholder="e.g., 'Speak with wisdom and authority', 'Sound excited and youthful', 'Use a French accent'",
        key=f"style_input_{persona_num}",
        height=80
    )
    setattr(st.session_state, style_key, style_prompt)
    
    persona_lang_key = f"persona_{persona_num}_language"
    if persona_lang_key not in st.session_state:
        st.session_state[persona_lang_key] = "Auto (Global Setting)"
    
    language_options = ["Auto (Global Setting)"] + list(SUPPORTED_LANGUAGES.keys())
    selected_language = st.selectbox(
        f"Language override for {persona_name}:",
        options=language_options,
        index=language_options.index(getattr(st.session_state, persona_lang_key, "Auto (Global Setting)")),
        key=f"language_select_{persona_num}",
        help="Override global language setting for this persona"
    )
    setattr(st.session_state, persona_lang_key, selected_language)

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
    <audio controls {autoplay_attr} style="width: 100%; margin: 5px 0;">
        <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
        Your browser does not support the audio element.
    </audio>
    """
