"""
Common UI components for Talk-To-Anyone application.
"""
import streamlit as st

def render_chat_messages():
    """
    Render the chat messages from the session state.
    """
    for msg in st.session_state.messages_display:
        with st.chat_message(msg["role"]):
            st.markdown(msg["text"])
            if "sources" in msg and msg["sources"]:
                with st.expander("Sources for this message"): 
                    for source in msg["sources"]:
                        st.markdown(
                            f"- [{source.get('title', 'Source')
                                      }]({source.get('uri')})"
                        )


def render_source_popover():
    """
    Render the sources popover in the header.
    """
    header_left, header_right = st.columns([0.85, 0.15])
    
    with header_left:
        if st.session_state.chat_mode == "Single Persona Chat":
            st.markdown(f"### Chatting with: {st.session_state.persona_1_name}")
        else: 
            st.markdown(f"### Persona Room: {st.session_state.persona_1_name} & {st.session_state.persona_2_name}")

    with header_right:
        with st.popover("📚 Sources", use_container_width=True):
            # content popover
            st.subheader("Collected Sources")
            if st.session_state.all_sources:
                sorted_sources = sorted(
                    st.session_state.all_sources, 
                    key=lambda s: (s.get('title') or s.get('uri', '')).lower()
                )
                for source_item in sorted_sources: 
                    title = source_item.get('title') or source_item.get('uri', 'Source')
                    uri = source_item.get('uri')
                    if uri:
                        st.markdown(f"- [{title}]({uri})")
            else:
                st.markdown("No sources collected yet.")
