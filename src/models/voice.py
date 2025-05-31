"""
Voice generation functionality for Talk-To-Anyone application using Gemini TTS.
"""
import streamlit as st
import wave
import io
from google.genai import types

VOICE_OPTIONS = {
    "Zephyr": "Bright",
    "Puck": "Upbeat", 
    "Charon": "Informative",
    "Kore": "Firm",
    "Fenrir": "Excitable",
    "Leda": "Youthful",
    "Orus": "Firm",
    "Aoede": "Breezy",
    "Callirrhoe": "Easy-going",
    "Autonoe": "Bright",
    "Enceladus": "Breathy",
    "Iapetus": "Clear",
    "Umbriel": "Easy-going",
    "Algieba": "Smooth",
    "Despina": "Smooth",
    "Erinome": "Clear",
    "Algenib": "Gravelly",
    "Rasalgethi": "Informative",
    "Laomedeia": "Upbeat",
    "Achernar": "Soft",
    "Alnilam": "Firm",
    "Schedar": "Even",
    "Gacrux": "Mature",
    "Pulcherrima": "Forward",
    "Achird": "Friendly",
    "Zubenelgenubi": "Casual",
    "Vindemiatrix": "Gentle",
    "Sadachbia": "Lively",
    "Sadaltager": "Knowledgeable",
    "Sulafat": "Warm"
}

def create_wave_file_data(pcm_data, channels=1, rate=24000, sample_width=2):
    """
    Create wave file data in memory from PCM data.
    
    Args:
        pcm_data: Raw PCM audio data
        channels: Number of audio channels
        rate: Sample rate
        sample_width: Sample width in bytes
        
    Returns:
        bytes: Wave file data
    """
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)
    return buffer.getvalue()

def generate_single_voice_audio(client, text, voice_name, style_prompt=""):
    """
    Generate single-speaker audio from text using Gemini TTS.
    
    Args:
        client: The Gemini API client
        text (str): Text to convert to speech
        voice_name (str): Name of the voice to use
        style_prompt (str): Optional style instructions
        
    Returns:
        bytes: Wave file data, or None if an error occurred
    """
    try:
        # Combine style prompt with text if provided
        if style_prompt:
            full_prompt = f"{style_prompt}: {text}"
        else:
            full_prompt = text
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name,
                        )
                    )
                ),
            )
        )
        
        if response.candidates and response.candidates[0].content.parts:
            pcm_data = response.candidates[0].content.parts[0].inline_data.data
            return create_wave_file_data(pcm_data)
        
        return None
        
    except Exception as e:
        st.error(f"Error generating voice audio: {e}")
        return None

def generate_multi_voice_audio(client, conversation_text, speaker_configs):
    """
    Generate multi-speaker audio from conversation text.
    
    Args:
        client: The Gemini API client
        conversation_text (str): Formatted conversation text
        speaker_configs (list): List of speaker configurations
        
    Returns:
        bytes: Wave file data, or None if an error occurred
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=conversation_text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=speaker_configs
                    )
                )
            )
        )
        
        if response.candidates and response.candidates[0].content.parts:
            pcm_data = response.candidates[0].content.parts[0].inline_data.data
            return create_wave_file_data(pcm_data)
        
        return None
        
    except Exception as e:
        st.error(f"Error generating multi-speaker audio: {e}")
        return None

def create_speaker_config(speaker_name, voice_name):
    """
    Create a speaker configuration for multi-speaker TTS.
    
    Args:
        speaker_name (str): Name of the speaker
        voice_name (str): Voice to use for this speaker
        
    Returns:
        SpeakerVoiceConfig: Configuration object
    """
    return types.SpeakerVoiceConfig(
        speaker=speaker_name,
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name=voice_name,
            )
        )
    )

def get_voice_style_suggestions(persona_description):
    """
    Suggest appropriate voice and style based on persona description.
    
    Args:
        persona_description (str): The persona's description
        
    Returns:
        dict: Suggested voice name and style prompt
    """
    description_lower = persona_description.lower()
    
    # keyword abased matching
    if any(word in description_lower for word in ['wise', 'professor', 'scholar', 'ancient']):
        return {"voice": "Gacrux", "style": "Speak in a wise and measured tone"}
    elif any(word in description_lower for word in ['young', 'energetic', 'excited', 'enthusiastic']):
        return {"voice": "Fenrir", "style": "Speak with excitement and energy"}
    elif any(word in description_lower for word in ['calm', 'peaceful', 'gentle', 'soft']):
        return {"voice": "Achernar", "style": "Speak in a calm and gentle manner"}
    elif any(word in description_lower for word in ['authoritative', 'leader', 'commander', 'strong']):
        return {"voice": "Kore", "style": "Speak with authority and confidence"}
    elif any(word in description_lower for word in ['mysterious', 'dark', 'gothic', 'spooky']):
        return {"voice": "Enceladus", "style": "Speak in a mysterious whisper"}
    elif any(word in description_lower for word in ['friendly', 'warm', 'kind', 'cheerful']):
        return {"voice": "Achird", "style": "Speak cheerfully and warmly"}
    else:
        return {"voice": "Zephyr", "style": "Speak naturally"}
