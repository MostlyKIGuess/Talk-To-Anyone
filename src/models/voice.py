"""
Voice generation functionality for Talk-To-Anyone application using Gemini TTS.
"""
import streamlit as st
import wave
import io
from google.genai import types

VOICE_OPTIONS = {
    # Female voices
    "Zephyr": {"gender": "female", "style": "Bright", "personality": "cheerful, optimistic"},
    "Kore": {"gender": "female", "style": "Firm", "personality": "strong, commanding"},
    "Leda": {"gender": "female", "style": "Youthful", "personality": "young, vibrant"},
    "Aoede": {"gender": "female", "style": "Breezy", "personality": "light, carefree"},
    "Callirrhoe": {"gender": "female", "style": "Easy-going", "personality": "relaxed, natural"},
    "Autonoe": {"gender": "female", "style": "Bright", "personality": "lively, spirited"},
    "Umbriel": {"gender": "female", "style": "Easy-going", "personality": "relaxed, versatile"},
    "Algieba": {"gender": "female", "style": "Smooth", "personality": "elegant, refined"},
    "Despina": {"gender": "female", "style": "Smooth", "personality": "graceful, polished"},
    "Erinome": {"gender": "female", "style": "Clear", "personality": "articulate, precise"},
    "Laomedeia": {"gender": "female", "style": "Upbeat", "personality": "enthusiastic, positive"},
    "Schedar": {"gender": "female", "style": "Even", "personality": "balanced, steady"},
    "Pulcherrima": {"gender": "female", "style": "Forward", "personality": "confident, assertive"},
    "Achird": {"gender": "female", "style": "Friendly", "personality": "warm, approachable"},
    "Vindemiatrix": {"gender": "female", "style": "Gentle", "personality": "soft, nurturing"},
    "Sadachbia": {"gender": "female", "style": "Lively", "personality": "energetic, spirited"},
    "Sulafat": {"gender": "female", "style": "Warm", "personality": "caring, compassionate"},
    "Achernar": {"gender": "female", "style": "Soft", "personality": "gentle, calm"},
    
    # Male voices
    "Puck": {"gender": "male", "style": "Upbeat", "personality": "energetic, youthful"},
    "Charon": {"gender": "male", "style": "Informative", "personality": "knowledgeable, authoritative"},
    "Fenrir": {"gender": "male", "style": "Excitable", "personality": "enthusiastic, dynamic"},
    "Orus": {"gender": "male", "style": "Firm", "personality": "strong, decisive"},
    "Enceladus": {"gender": "male", "style": "Breathy", "personality": "mysterious, soft-spoken"},
    "Iapetus": {"gender": "male", "style": "Clear", "personality": "articulate, professional"},
    "Algenib": {"gender": "male", "style": "Gravelly", "personality": "rough, experienced"},
    "Rasalgethi": {"gender": "male", "style": "Informative", "personality": "scholarly, wise"},
    "Alnilam": {"gender": "male", "style": "Firm", "personality": "confident, solid"},
    "Gacrux": {"gender": "male", "style": "Mature", "personality": "wise, experienced"},
    "Zubenelgenubi": {"gender": "male", "style": "Casual", "personality": "relaxed, friendly"},
    "Sadaltager": {"gender": "male", "style": "Knowledgeable", "personality": "intelligent, scholarly"}
}

SUPPORTED_LANGUAGES = {
    "Arabic (Egyptian)": "ar-EG",
    "Bengali (Bangladesh)": "bn-BD", 
    "Dutch (Netherlands)": "nl-NL",
    "English (US)": "en-US",
    "English (India)": "en-IN",
    "French (France)": "fr-FR",
    "German (Germany)": "de-DE",
    "Hindi (India)": "hi-IN",
    "Indonesian (Indonesia)": "id-ID",
    "Italian (Italy)": "it-IT",
    "Japanese (Japan)": "ja-JP",
    "Korean (Korea)": "ko-KR",
    "Marathi (India)": "mr-IN",
    "Polish (Poland)": "pl-PL",
    "Portuguese (Brazil)": "pt-BR",
    "Romanian (Romania)": "ro-RO",
    "Russian (Russia)": "ru-RU",
    "Spanish (US)": "es-US",
    "Tamil (India)": "ta-IN",
    "Telugu (India)": "te-IN",
    "Thai (Thailand)": "th-TH",
    "Turkish (Turkey)": "tr-TR",
    "Ukrainian (Ukraine)": "uk-UA",
    "Vietnamese (Vietnam)": "vi-VN"
}

def get_voices_by_gender(gender=None):
    """
    Get voices filtered by gender.
    
    Args:
        gender (str): 'male', 'female', or None for all voices
        
    Returns:
        dict: Filtered voice options
    """
    if gender is None:
        return VOICE_OPTIONS
    
    return {name: info for name, info in VOICE_OPTIONS.items() 
            if info["gender"] == gender}

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

def generate_single_voice_audio(client, text, voice_name, style_prompt="", language_hint=""):
    """
    Generate single-speaker audio from text using Gemini TTS.
    
    Args:
        client: The Gemini API client
        text (str): Text to convert to speech
        voice_name (str): Name of the voice to use
        style_prompt (str): Optional style instructions
        language_hint (str): Optional language hint for better pronunciation
        
    Returns:
        bytes: Wave file data, or None if an error occurred
    """
    try:
        full_prompt = text
        if style_prompt:
            full_prompt = f"{style_prompt}: {text}"
        
        if language_hint:
            full_prompt = f"Speak in {language_hint}. {full_prompt}"
        
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

def detect_persona_gender(persona_description):
    """
    Attempt to detect gender from persona description.
    
    Args:
        persona_description (str): The persona's description
        
    Returns:
        str: 'male', 'female', or 'neutral'
    """
    description_lower = persona_description.lower()
    
    # Male indicators
    male_keywords = ['he', 'him', 'his', 'man', 'male', 'father', 'king', 'emperor', 'prince', 
                     'lord', 'sir', 'gentleman', 'boy', 'son', 'brother', 'uncle', 'grandfather']
    
    # Female indicators  
    female_keywords = ['she', 'her', 'woman', 'female', 'mother', 'queen', 'empress', 'princess',
                       'lady', 'madam', 'girl', 'daughter', 'sister', 'aunt', 'grandmother']
    
    male_count = sum(1 for keyword in male_keywords if keyword in description_lower)
    female_count = sum(1 for keyword in female_keywords if keyword in description_lower)
    
    if male_count > female_count and male_count > 0:
        return "male"
    elif female_count > male_count and female_count > 0:
        return "female"
    else:
        return "neutral"

def get_voice_style_suggestions(persona_description):
    """
    Suggest appropriate voice and style based on persona description with gender awareness.
    
    Args:
        persona_description (str): The persona's description
        
    Returns:
        dict: Suggested voice name, style prompt, and reasoning
    """
    description_lower = persona_description.lower()
    detected_gender = detect_persona_gender(persona_description)
    
    gender_voices = get_voices_by_gender(detected_gender)
    if not gender_voices:
        gender_voices = VOICE_OPTIONS
    
    suggestions = []
    
    # Wise/scholarly characters
    if any(word in description_lower for word in ['wise', 'professor', 'scholar', 'ancient', 'sage', 'philosopher', 'teacher']):
        if detected_gender == "male":
            suggestions.append({"voice": "Gacrux", "style": "Speak in a wise and measured tone with authority", "reason": "Mature male voice for wise character"})
            suggestions.append({"voice": "Sadaltager", "style": "Speak with scholarly wisdom", "reason": "Knowledgeable male voice"})
        elif detected_gender == "female":
            suggestions.append({"voice": "Kore", "style": "Speak with firm wisdom and authority", "reason": "Strong female voice for authority"})
            suggestions.append({"voice": "Erinome", "style": "Speak clearly with scholarly precision", "reason": "Clear female voice for academic tone"})
    
    # Young/energetic characters
    elif any(word in description_lower for word in ['young', 'energetic', 'excited', 'enthusiastic', 'child', 'teenager']):
        if detected_gender == "male":
            suggestions.append({"voice": "Fenrir", "style": "Speak with excitement and youthful energy", "reason": "Excitable male voice"})
            suggestions.append({"voice": "Puck", "style": "Speak with upbeat enthusiasm", "reason": "Upbeat male voice"})
        elif detected_gender == "female":
            suggestions.append({"voice": "Leda", "style": "Speak with youthful excitement", "reason": "Youthful female voice"})
            suggestions.append({"voice": "Sadachbia", "style": "Speak with lively energy", "reason": "Lively female voice"})
    
    # Calm/peaceful characters
    elif any(word in description_lower for word in ['calm', 'peaceful', 'gentle', 'soft', 'serene', 'tranquil']):
        if detected_gender == "male":
            suggestions.append({"voice": "Enceladus", "style": "Speak softly with a breathy, peaceful tone", "reason": "Breathy male voice for peaceful tone"})
            suggestions.append({"voice": "Zubenelgenubi", "style": "Speak in a calm and casual manner", "reason": "Casual male voice"})
        elif detected_gender == "female":
            suggestions.append({"voice": "Achernar", "style": "Speak in a calm and gentle manner", "reason": "Soft female voice"})
            suggestions.append({"voice": "Vindemiatrix", "style": "Speak gently with nurturing warmth", "reason": "Gentle female voice"})
    
    # Authoritative/leader characters
    elif any(word in description_lower for word in ['authoritative', 'leader', 'commander', 'strong', 'king', 'queen', 'ruler', 'boss']):
        if detected_gender == "male":
            suggestions.append({"voice": "Orus", "style": "Speak with commanding authority", "reason": "Firm male voice for leadership"})
            suggestions.append({"voice": "Alnilam", "style": "Speak with confident strength", "reason": "Strong male voice"})
        elif detected_gender == "female":
            suggestions.append({"voice": "Kore", "style": "Speak with firm authority and confidence", "reason": "Commanding female voice"})
            suggestions.append({"voice": "Pulcherrima", "style": "Speak with forward confidence", "reason": "Assertive female voice"})
    
    # Mysterious/dark characters
    elif any(word in description_lower for word in ['mysterious', 'dark', 'gothic', 'spooky', 'shadow', 'enigmatic']):
        if detected_gender == "male":
            suggestions.append({"voice": "Enceladus", "style": "Speak in a mysterious whisper", "reason": "Breathy male voice for mystery"})
            suggestions.append({"voice": "Algenib", "style": "Speak with a gravelly, mysterious tone", "reason": "Gravelly male voice"})
        elif detected_gender == "female":
            suggestions.append({"voice": "Despina", "style": "Speak smoothly with mysterious elegance", "reason": "Smooth female voice for intrigue"})
            suggestions.append({"voice": "Algieba", "style": "Speak with refined mystery", "reason": "Elegant female voice"})
    
    # Friendly/warm characters
    elif any(word in description_lower for word in ['friendly', 'warm', 'kind', 'cheerful', 'caring', 'loving']):
        if detected_gender == "male":
            suggestions.append({"voice": "Zubenelgenubi", "style": "Speak casually and warmly", "reason": "Casual male voice"})
            suggestions.append({"voice": "Puck", "style": "Speak with upbeat friendliness", "reason": "Upbeat male voice"})
        elif detected_gender == "female":
            suggestions.append({"voice": "Achird", "style": "Speak with friendly warmth", "reason": "Friendly female voice"})
            suggestions.append({"voice": "Sulafat", "style": "Speak with caring warmth", "reason": "Warm female voice"})
    
    # Default suggestions based on gender
    if not suggestions:
        if detected_gender == "male":
            suggestions.append({"voice": "Puck", "style": "Speak naturally with an upbeat tone", "reason": "Default male voice"})
        elif detected_gender == "female":
            suggestions.append({"voice": "Zephyr", "style": "Speak naturally with brightness", "reason": "Default female voice"})
        else:
            # For neutral, pick a balanced option
            suggestions.append({"voice": "Umbriel", "style": "Speak naturally in an easy-going manner", "reason": "Versatile voice"})
    
    # Return the best suggestion
    best_suggestion = suggestions[0] if suggestions else {"voice": "Zephyr", "style": "Speak naturally", "reason": "Fallback voice"}
    
    return {
        "voice": best_suggestion["voice"],
        "style": best_suggestion["style"],
        "gender": detected_gender,
        "reason": best_suggestion["reason"],
        "alternatives": suggestions[1:3] if len(suggestions) > 1 else []
    }
