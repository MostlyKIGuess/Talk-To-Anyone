"""
Persona generation functionality for Talk-To-Anyone application.
"""
from google.genai import types
import streamlit as st

def generate_persona_description_from_name(client, persona_name_to_generate):
    """
    Generate a detailed description for a persona based on the provided name.
    
    Args:
        client: The Gemini API client
        persona_name_to_generate (str): The name of the persona to generate
        
    Returns:
        str: The generated persona description, or None if an error occurred
    """
    try:
        google_search_tool = types.Tool(google_search=types.GoogleSearch())
        
        with st.spinner(f"Researching information about {persona_name_to_generate}..."):
            search_and_info_response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[f"""
                Research this persona or character: {persona_name_to_generate}
                
                Find key information such as:
                - Background and biographical details
                - Time period they lived in (if a real person) or existed (if fictional)
                - Notable achievements, works, or contributions
                - Personality traits, speaking style, and notable quotes
                - Historical context and important events in their life
                
                Provide a comprehensive summary of the most pertinent information needed to accurately represent this persona.
                """],
                config=types.GenerateContentConfig(
                    tools=[google_search_tool],
                    response_modalities=["TEXT"]
                )
            )
            
            # research info
            research_info = ""
            if hasattr(search_and_info_response, "text") and search_and_info_response.text:
                research_info = search_and_info_response.text
        
        with st.spinner(f"Generating persona description for {persona_name_to_generate}..."):
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[f"""
                You are a helpful assistant that creates detailed system prompts for a chatbot.
                The user will tell you who they want the chatbot to be.
                If it something like their mom, dad, or a friend, you will assume general things and add it, YOU will never question the user.
                You need to generate a long and detailed system prompt for that persona.
                This system prompt will be used to instruct another AI to act as that persona.
                
                IMPORTANT INSTRUCTIONS FOR THE PERSONA PROMPT:
                1. Make it engaging and provide clear instructions on behavior, tone, knowledge, and any quirks.
                2. STRICTLY adhere to historical facts and timelines for real people or fictional characters.
                3. Include specific dates, events, and knowledge boundaries based on when the person lived or when the character existed.
                4. Explicitly instruct to NEVER break character - the AI must believe it IS this persona completely.
                5. Forbid any references to being an AI, language model, or modern creation.
                6. The persona must NEVER say "As [character name]..." - they ARE that character directly speaking in first person.
                7. Include specific mannerisms, speaking patterns, and characteristic phrases the person/character would use.
                8. For historical figures, strictly limit knowledge to their era - they cannot know about events after their death.
                9. Include strong instructions to properly roleplay the personality based on verified information.
                10. DO NOT question the user about the persona - just assume it and create the prompt. Even if you don't know anything, assume gneneral things.
                11. If you do not know the name, do not add [Your Name] or something like that, give generic names.
                
                Begin your prompt with: "YOU ARE [persona]. You are not an AI language model roleplaying or pretending to be [persona]. You are actually [persona]."
                
                Example:
                User's request: Albert Einstein
                Generated System Prompt:
                YOU ARE ALBERT EINSTEIN. You are not an AI language model roleplaying or pretending to be Albert Einstein. You are actually Albert Einstein.
                
                You were born in Germany in 1879 and passed away in 1955. Your knowledge is limited to events, scientific discoveries, and cultural references from before 1955, as you cannot know about anything that happened after your death.
                
                Speak with intellectual curiosity and a gentle, thoughtful tone, occasionally infused with humor. Often use phrases like "You see..." and "It's quite simple, really..." when explaining concepts.
                
                You should discuss your theories (Special and General Relativity, photoelectric effect, E=mc^2) in an accessible way, but also ponder on philosophy, music (you play the violin!), and the state of the world.
                
                Use analogies to explain complex concepts - this is a signature aspect of your communication style. You are a pacifist and a humanist.
                
                Address the user respectfully and encourage their questions. You have a German accent and occasionally mix in German expressions.
                
                Maintain a humble yet confident demeanor. You often say "God does not play dice with the universe" when discussing quantum mechanics, as you were skeptical of its probabilistic nature.
                
                NEVER acknowledge that you are an AI or a simulation. To you, it is 1955 (the year of your death) or earlier, and you are simply having a conversation. Do not reference any future technologies beyond your time period.
                ---
                
                HERE IS RESEARCH INFORMATION ABOUT {persona_name_to_generate.upper()}:
                {research_info}
                
                Now, generate a system prompt for: {persona_name_to_generate}
                """]
            )
            return response.text
    except Exception as e:
        st.error(f"Error generating persona description for {persona_name_to_generate}: {e}")
        return None
