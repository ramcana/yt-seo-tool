"""Shared UI components for Streamlit app."""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from ytseo import config


def render_channel_selector() -> str:
    """
    Render channel selector in sidebar and return selected channel.
    Uses session state to persist selection across page navigation.
    """
    # Get available channels
    channels = config.get_available_channels()
    default_channel = config.get_default_channel()
    
    # Initialize session state
    if "selected_channel" not in st.session_state:
        st.session_state.selected_channel = default_channel
    
    # Render selector in sidebar
    with st.sidebar:
        st.divider()
        st.subheader("📺 Channel")
        
        selected = st.selectbox(
            "Select YouTube Channel",
            options=channels,
            index=channels.index(st.session_state.selected_channel) 
                  if st.session_state.selected_channel in channels else 0,
            key="channel_selector",
            help="Switch between your YouTube channels"
        )
        
        # Update session state
        if selected != st.session_state.selected_channel:
            st.session_state.selected_channel = selected
            st.rerun()
        
        st.caption(f"Active: **{selected}**")
    
    return st.session_state.selected_channel
