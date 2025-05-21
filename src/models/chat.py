"""
Chat session management for Talk-To-Anyone application.
"""
import streamlit as st
from google.genai import types

def initialize_chat_session(client, persona_description):
    """
    Initialize a chat session with the given persona description.
    
    Args:
        client: The Gemini API client
        persona_description (str): The system prompt for the persona
        
    Returns:
        object: The chat session object, or None if an error occurred
    """
    try:
        google_search_tool = types.Tool(google_search=types.GoogleSearch())
        chat_session = client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=persona_description,
                tools=[google_search_tool],
                response_modalities=["TEXT"],
            ),
        )
        return chat_session
    except Exception as e:
        st.error(f"Failed to initialize chat model: {e}")
        return None


def extract_sources_from_response(response):
    """
    Extract source references from a Gemini API response.
    
    Args:
        response: The Gemini API response object
        
    Returns:
        list: A list of source dictionaries, each containing 'uri' and 'title'
    """
    sources_data = []
    candidate = None
    if hasattr(response, "candidates") and response.candidates:
        candidate = response.candidates[0]

    grounding_metadata = None
    if (
        candidate
        and hasattr(candidate, "grounding_metadata")
        and candidate.grounding_metadata
    ):
        grounding_metadata = candidate.grounding_metadata

    if grounding_metadata and hasattr(grounding_metadata, "grounding_chunks"):
        grounding_chunks_data = grounding_metadata.grounding_chunks
        if grounding_chunks_data is not None:
            for chunk in grounding_chunks_data:
                if chunk and hasattr(chunk, "web") and chunk.web:
                    web_info = chunk.web
                    uri = getattr(web_info, "uri", None)
                    title = getattr(web_info, "title", None)
                    if uri:
                        sources_data.append(
                            {"uri": uri, "title": title if title else "Source"}
                        )
    return sources_data
