import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error(
        "GEMINI_API_KEY not found in .env file. Please create a .env file with your API key (e.g., GEMINI_API_KEY=your_actual_key)."
    )
    st.stop()

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(
        f"Failed to configure Gemini API: {
            e
        }. Ensure your API key is correct and the google-generativeai package is installed."
    )
    st.stop()


def generate_persona_description_from_name(persona_name_to_generate):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[f"""
            You are a helpful assistant that creates detailed system prompts for a chatbot.
            The user will tell you who they want the chatbot to be.
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
            Now, generate a system prompt for: {persona_name_to_generate}
            """]
        )
        return response.text
    except Exception as e:
        st.error(f"Error generating persona description for {persona_name_to_generate}: {e}")
        return None



def initialize_chat_session(persona_description):
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


#  sources boom
def extract_sources_from_response(response):
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


#  session states
if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "messages_display" not in st.session_state:
    st.session_state.messages_display = []
if "developer_mode" not in st.session_state:
    st.session_state.developer_mode = False
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = "Single Persona Chat"

# Persona 1
if "persona_1_name" not in st.session_state:
    st.session_state.persona_1_name = ""
if "persona_1_description" not in st.session_state:
    st.session_state.persona_1_description = None
if "persona_1_session" not in st.session_state:
    st.session_state.persona_1_session = None

# Persona 2 (for Persona Room)
if "persona_2_name" not in st.session_state:
    st.session_state.persona_2_name = ""
if "persona_2_description" not in st.session_state:
    st.session_state.persona_2_description = None
if "persona_2_session" not in st.session_state:
    st.session_state.persona_2_session = None

#  room relevant states 
if "action_buttons_visible" not in st.session_state:
    st.session_state.action_buttons_visible = False
if "last_actor" not in st.session_state:  # "User", persona_1_name, persona_2_name
    st.session_state.last_actor = None
if "last_message_text" not in st.session_state:  # Text of the last message for context
    st.session_state.last_message_text = None


st.title("Talk To Anyone 🗣️")
st.session_state.developer_mode = st.sidebar.toggle(
    "Developer Mode", value=st.session_state.developer_mode
)

current_chat_mode_selection = st.sidebar.radio(
    "Select Chat Mode:",
    ("Single Persona Chat", "Persona Room"),
    index=0 if st.session_state.chat_mode == "Single Persona Chat" else 1,
    key="chat_mode_selection_radio",
)

# If chat mode changes, reset relevant states
if current_chat_mode_selection != st.session_state.chat_mode:
    st.session_state.chat_mode = current_chat_mode_selection
    st.session_state.start_chat = False
    st.session_state.messages_display = []
    st.session_state.persona_1_name = ""
    st.session_state.persona_1_description = None
    st.session_state.persona_1_session = None
    st.session_state.persona_2_name = ""
    st.session_state.persona_2_description = None
    st.session_state.persona_2_session = None
    st.session_state.action_buttons_visible = False
    st.session_state.last_actor = None
    st.session_state.last_message_text = None
    st.rerun()


if not st.session_state.start_chat:
    if st.session_state.chat_mode == "Single Persona Chat":
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
                f"Generating persona description for {
                    st.session_state.persona_1_name
                }..."
            ):
                st.session_state.persona_1_description = (
                    generate_persona_description_from_name(
                        st.session_state.persona_1_name
                    )
                )

        if st.session_state.persona_1_description:
            if st.session_state.developer_mode:
                st.subheader("Generated Persona Description (System Prompt):")
                st.markdown(st.session_state.persona_1_description)

            if st.button(
                f"👍 Yes, I want to talk to {st.session_state.persona_1_name}!",
                key="confirm_single_persona_btn",
            ):
                st.session_state.persona_1_session = initialize_chat_session(
                    st.session_state.persona_1_description
                )
                if st.session_state.persona_1_session:
                    st.session_state.start_chat = True
                    st.session_state.messages_display = []
                    st.rerun()
                else:
                    st.error("Failed to initialize chat session for persona.")

    elif st.session_state.chat_mode == "Persona Room":
        st.subheader("Define the Personas for the Room")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Persona 1")
            p1_room_name_input = st.text_input(
                "Name for Persona 1",
                value=st.session_state.persona_1_name,
                key="persona_1_room_name_text_input",
            )
            st.session_state.persona_1_name = p1_room_name_input
        with col2:
            st.markdown("#### Persona 2")
            p2_room_name_input = st.text_input(
                "Name for Persona 2",
                value=st.session_state.persona_2_name,
                key="persona_2_room_name_text_input",
            )
            st.session_state.persona_2_name = p2_room_name_input

        if st.button(
            "✨ Generate Both Personas",
            disabled=not (
                st.session_state.persona_1_name and st.session_state.persona_2_name
            ),
            key="generate_room_personas_btn",
        ):
            if st.session_state.persona_1_name:
                with st.spinner(
                    f"Generating persona description for {
                        st.session_state.persona_1_name
                    }..."
                ):
                    st.session_state.persona_1_description = (
                        generate_persona_description_from_name(
                            st.session_state.persona_1_name
                        )
                    )
            if st.session_state.persona_2_name:
                with st.spinner(
                    f"Generating persona description for {
                        st.session_state.persona_2_name
                    }..."
                ):
                    st.session_state.persona_2_description = (
                        generate_persona_description_from_name(
                            st.session_state.persona_2_name
                        )
                    )

        if (
            st.session_state.persona_1_description
            and st.session_state.persona_2_description
        ):
            if st.session_state.developer_mode:
                st.subheader("Generated Persona 1 Description:")
                st.markdown(st.session_state.persona_1_description)
                st.subheader("Generated Persona 2 Description:")
                st.markdown(st.session_state.persona_2_description)

            if st.button(
                f"👍 Yes, let {st.session_state.persona_1_name} and {
                    st.session_state.persona_2_name
                } talk!",
                key="confirm_room_personas_btn",
            ):
                st.session_state.persona_1_session = initialize_chat_session(
                    st.session_state.persona_1_description
                )
                st.session_state.persona_2_session = initialize_chat_session(
                    st.session_state.persona_2_description
                )

                if (
                    st.session_state.persona_1_session
                    and st.session_state.persona_2_session
                ):
                    st.session_state.start_chat = True
                    st.session_state.messages_display = []
                    st.rerun()
                else:
                    st.error(
                        "Failed to initialize chat sessions for one or both personas."
                    )

if st.session_state.start_chat:
    if st.session_state.chat_mode == "Single Persona Chat":
        _, right_col = st.columns([3, 1])
        with right_col:
            st.markdown(f"**Chatting as: {st.session_state.persona_1_name}**")
    else:
        _, right_col = st.columns([3, 1])
        with right_col:
            st.markdown(f"**Persona Room: {st.session_state.persona_1_name} & {st.session_state.persona_2_name}**")
            
    for msg in st.session_state.messages_display:
        with st.chat_message(msg["role"]):
            st.markdown(msg["text"])
            if "sources" in msg and msg["sources"]:
                st.markdown("--- \n*Sources:*")
                for source in msg["sources"]:
                    st.markdown(
                        f"- [{source.get('title', 'Source')
                              }]({source.get('uri')})"
                    )

    if st.session_state.chat_mode == "Single Persona Chat":
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
                            message = {
                                "role": st.session_state.persona_1_name,
                                "text": model_response_text,
                                "sources": sources,
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

    elif st.session_state.chat_mode == "Persona Room":
        if (
            st.session_state.persona_1_session
            and st.session_state.persona_2_session
            and st.session_state.persona_1_name
            and st.session_state.persona_2_name
        ):
            st.subheader(
                f"Persona Room: {st.session_state.persona_1_name} & {
                    st.session_state.persona_2_name
                }"
            )

            user_prompt = st.chat_input(
                "Your message for the room...", key="room_chat_input"
            )

            if user_prompt:
                st.session_state.messages_display.append(
                    {"role": "User", "text": user_prompt, "sources": []}
                )
                st.session_state.last_actor = "User"
                st.session_state.last_message_text = user_prompt
                st.session_state.action_buttons_visible = True
                st.rerun()

            if (
                st.session_state.action_buttons_visible
                and st.session_state.last_message_text
            ):
                st.markdown("---")
                st.write("Choose who speaks next:")
                cols = st.columns(2)

                def handle_persona_response(
                    persona_session, persona_name, responding_to_actor_name, prompt_text
                ):
                    with st.spinner(f"{persona_name} is thinking..."):
                        try:
                            # The prompt_text is the last message uttered, which the persona will respond to.
                            # The persona's own chat history is maintained by its session object.
                            response = persona_session.send_message(
                                prompt_text)
                            model_text = "No text in response."
                            sources = []
                            if response:
                                model_text = getattr(
                                    response, "text", "No text in response."
                                )
                                sources = extract_sources_from_response(
                                    response)

                            if model_text != "No text in response.":
                                st.session_state.messages_display.append(
                                    {
                                        "role": persona_name,
                                        "text": model_text,
                                        "sources": sources,
                                    }
                                )
                                st.session_state.last_actor = persona_name
                                st.session_state.last_message_text = model_text
                            else:
                                st.warning(
                                    f"{persona_name} did not provide a text response."
                                )
                                # last_actor and last_message_text remain from the previous turn,
                                # allowing the other persona or user to act based on that previous message.
                        except Exception as e:
                            st.error(f"Error from {persona_name}: {e}")
                        st.session_state.action_buttons_visible = True
                        st.rerun()
                with cols[0]:
                    p1_name = st.session_state.persona_1_name
                    p2_name = st.session_state.persona_2_name
                    if st.session_state.last_actor == "User":
                        if st.button(
                            f"Let {p1_name} respond to User",
                            key="p1_responds_user_btn",
                            use_container_width=True,
                        ):
                            handle_persona_response(
                                st.session_state.persona_1_session,
                                p1_name,
                                "User",
                                st.session_state.last_message_text,
                            )
                    elif st.session_state.last_actor == p2_name:
                        if st.button(
                            f"Let {p1_name} respond to {p2_name}",
                            key="p1_responds_p2_btn",
                            use_container_width=True,
                        ):
                            handle_persona_response(
                                st.session_state.persona_1_session,
                                p1_name,
                                p2_name,
                                st.session_state.last_message_text,
                            )

                with cols[1]:
                    if st.session_state.last_actor == "User":
                        if st.button(
                            f"Let {p2_name} respond to User",
                            key="p2_responds_user_btn",
                            use_container_width=True,
                        ):
                            handle_persona_response(
                                st.session_state.persona_2_session,
                                p2_name,
                                "User",
                                st.session_state.last_message_text,
                            )
                    elif st.session_state.last_actor == p1_name:
                        if st.button(
                            f"Let {p2_name} respond to {p1_name}",
                            key="p2_responds_p1_btn",
                            use_container_width=True,
                        ):
                            handle_persona_response(
                                st.session_state.persona_2_session,
                                p2_name,
                                p1_name,
                                st.session_state.last_message_text,
                            )
        else:
            st.warning(
                "Chat sessions or persona names are missing for Persona Room.")
            st.rerun()

    if st.sidebar.button("⬅️ New Chat / Exit Room", key="exit_chat_btn"):
        st.session_state.start_chat = False
        st.session_state.messages_display = []
        st.session_state.persona_1_name = ""
        st.session_state.persona_1_description = None
        st.session_state.persona_1_session = None
        st.session_state.persona_2_name = ""
        st.session_state.persona_2_description = None
        st.session_state.persona_2_session = None
        st.session_state.action_buttons_visible = False
        st.session_state.last_actor = None
        st.session_state.last_message_text = None
        st.rerun()

elif st.session_state.start_chat:
    required_p1 = (
        st.session_state.persona_1_description and st.session_state.persona_1_session
    )
    required_p2_room = (
        st.session_state.persona_2_description and st.session_state.persona_2_session
    )

    conditions_met = False
    if st.session_state.chat_mode == "Single Persona Chat" and required_p1:
        conditions_met = True
    elif (
        st.session_state.chat_mode == "Persona Room"
        and required_p1
        and required_p2_room
    ):
        conditions_met = True

    if not conditions_met:
        st.warning(
            "Persona description(s) or chat session(s) are missing. Please define persona(s) first."
        )
        st.session_state.start_chat = False
        st.rerun()
