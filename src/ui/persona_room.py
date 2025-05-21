"""
Persona Room UI components for Talk-To-Anyone application.
"""
import streamlit as st
from ..models import generate_persona_description_from_name, initialize_chat_session, extract_sources_from_response

def render_persona_room_setup(client):
    """
    Render the UI for setting up a persona room with two personas.
    
    Args:
        client: The Gemini API client
        
    Returns:
        bool: True if chat should start, False otherwise
    """
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
                        client, st.session_state.persona_1_name
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
                        client, st.session_state.persona_2_name
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
                client, st.session_state.persona_1_description
            )
            st.session_state.persona_2_session = initialize_chat_session(
                client, st.session_state.persona_2_description
            )

            if (
                st.session_state.persona_1_session
                and st.session_state.persona_2_session
            ):
                st.session_state.start_chat = True
                st.session_state.messages_display = []
                st.session_state.all_sources = []
                return True
            else:
                st.error(
                    "Failed to initialize chat sessions for one or both personas."
                )
    
    return False


def handle_persona_room_interaction(client):
    """
    Handle the interaction for the persona room with two personas.
    
    Args:
        client: The Gemini API client
    """
    if (
        st.session_state.persona_1_session
        and st.session_state.persona_2_session
        and st.session_state.persona_1_name
        and st.session_state.persona_2_name
    ):
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
                        response = persona_session.send_message(prompt_text)
                        model_text = "No text in response."
                        sources = []
                        if response:
                            model_text = getattr(
                                response, "text", "No text in response."
                            )
                            sources = extract_sources_from_response(response)

                        existing_uris = {s['uri'] for s in st.session_state.all_sources if 'uri' in s}
                        for src in sources:
                            if src.get('uri') and src['uri'] not in existing_uris:
                                st.session_state.all_sources.append(src)
                                existing_uris.add(src['uri'])

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
        st.session_state.start_chat = False 
        st.rerun()
