import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found in .env file. Please create a .env file with your API key (e.g., GEMINI_API_KEY=your_actual_key).")
    st.stop()

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Failed to configure Gemini API: {e}. Ensure your API key is correct and the google-generativeai package is installed.")
    st.stop()

if "persona_description_generated" not in st.session_state:
    st.session_state.persona_description_generated = None
if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "messages_display" not in st.session_state:
    st.session_state.messages_display = []
if "persona_input_name" not in st.session_state:
    st.session_state.persona_input_name = ""
if "developer_mode" not in st.session_state:
    st.session_state.developer_mode = False

st.title("Talk To Anyone 🗣️")
st.session_state.developer_mode = st.toggle("Developer Mode", value=st.session_state.developer_mode)

if not st.session_state.start_chat:
    st.subheader("Who do you want to talk to?")
    persona_name_input = st.text_input(
        "E.g., Albert Einstein, a futuristic AI assistant, a pirate captain",
        value=st.session_state.persona_input_name,
        key="persona_name_text_input"
    )
    st.session_state.persona_input_name = persona_name_input

    if st.button("✨ Generate Persona", disabled=not persona_name_input):
        with st.spinner(f"Generating persona description for {persona_name_input}..."):
            try:
                persona_gen_model = genai.GenerativeModel("gemini-2.0-flash")
                
                prompt_for_persona_generation = f"""
                You are a helpful assistant that creates detailed system prompts for a chatbot.
                The user will tell you who they want the chatbot to be.
                You need to generate a long and detailed system prompt for that persona.
                This system prompt will be used to instruct another AI to act as that persona.
                Make it engaging and provide clear instructions on behavior, tone, knowledge, and any quirks. It can be a person, thing, object anything, personalities, or even fictional characters.
                You need to personify everything basically.

                Example:
                User's request: Albert Einstein
                Generated System Prompt:
                You are Albert Einstein, the world-renowned theoretical physicist who developed the theory of relativity.
                You were born in Germany in 1879 and passed away in 1955.
                Speak with intellectual curiosity and a gentle, thoughtful tone, occasionally infused with humor.
                You should be able to discuss your theories (Special and General Relativity, photoelectric effect, E=mc^2) in an accessible way,
                but also ponder on philosophy, music (you play the violin!), and the state of the world.
                Use analogies to explain complex concepts. You are a pacifist and a humanist.
                Address the user respectfully and encourage their questions.
                Avoid modern slang or knowledge of events after your passing.
                Maintain a humble yet confident demeanor.
                ---
                Now, generate a system prompt for: {persona_name_input}
                """
                
                response = persona_gen_model.generate_content(prompt_for_persona_generation)
                st.session_state.persona_description_generated = response.text
            except Exception as e:
                st.error(f"Error generating persona description: {e}")
                st.session_state.persona_description_generated = None

    if st.session_state.persona_description_generated:
        if st.session_state.developer_mode:
            st.subheader("Generated Persona Description (System Prompt):")
            st.markdown(st.session_state.persona_description_generated)
        
        if st.button(f"👍 Yes, I want to talk to {st.session_state.persona_input_name}!", key="confirm_persona"):
            st.session_state.start_chat = True
            st.session_state.messages_display = []
            
            try:
                chat_model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash-latest",
                    system_instruction=st.session_state.persona_description_generated
                )
                st.session_state.chat_session = chat_model.start_chat(history=[])
            except Exception as e:
                st.error(f"Failed to initialize chat model: {e}")
                st.session_state.start_chat = False
            st.rerun()

if st.session_state.start_chat and st.session_state.persona_description_generated and st.session_state.chat_session:
    st.subheader(f"Chatting as: {st.session_state.persona_input_name}")
    
    for msg in st.session_state.messages_display:
        with st.chat_message(msg["role"]):
            st.markdown(msg["text"])

    user_prompt = st.chat_input(f"Talk to {st.session_state.persona_input_name}...")

    if user_prompt:
        st.session_state.messages_display.append({"role": "User", "text": user_prompt})
        
        with st.chat_message("User"):
            st.markdown(user_prompt)

        with st.spinner(f"{st.session_state.persona_input_name} is thinking..."):
            try:
                response = st.session_state.chat_session.send_message(user_prompt)
                model_response_text = response.text
                
                st.session_state.messages_display.append({"role": st.session_state.persona_input_name, "text": model_response_text})
                
                st.rerun()

            except Exception as e:
                st.error(f"Error getting response from Gemini: {e}")
                if st.session_state.messages_display and st.session_state.messages_display[-1]["text"] == user_prompt:
                    st.session_state.messages_display.pop()

    if st.button("⬅️ Talk to someone else"):
        st.session_state.persona_description_generated = None
        st.session_state.start_chat = False
        st.session_state.chat_session = None
        st.session_state.messages_display = []
        st.session_state.persona_input_name = ""
        st.rerun()

elif st.session_state.start_chat and (not st.session_state.persona_description_generated or not st.session_state.chat_session):
    st.warning("Persona description or chat session is missing. Please define a persona first.")
    st.session_state.start_chat = False
    if st.button("Define Persona"):
        st.rerun()
