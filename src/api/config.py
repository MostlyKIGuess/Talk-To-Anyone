"""
API configuration for the Talk-To-Anyone application.
"""
import os
from dotenv import load_dotenv
from google import genai

def initialize_api():
    """
    Initialize the Gemini API client from environment variables.
    
    Returns:
        tuple: (client, error_message) - client is None if there's an error
    """
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    if not GEMINI_API_KEY:
        return None, "GEMINI_API_KEY not found in .env file. Please create a .env file with your API key (e.g., GEMINI_API_KEY=your_actual_key)."
    
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        return client, None
    except Exception as e:
        return None, f"Failed to configure Gemini API: {e}. Ensure your API key is correct and the google-generativeai package is installed."
