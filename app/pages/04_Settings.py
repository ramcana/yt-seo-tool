import os
import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ytseo.config import get_setting, get_available_channels
    from shared import render_channel_selector
except Exception:
    def get_setting(key: str, default=None):
        return os.environ.get(key, default)
    def get_available_channels():
        return ["@TheNewsForum"]

# Render channel selector
selected_channel = render_channel_selector()

st.title("⚙️ Settings")

st.subheader("📺 YouTube Configuration")
channels = get_available_channels()
st.write(f"**Available Channels:** {', '.join(channels)}")
st.write(f"**Active Channel:** {selected_channel}")
st.write(f"**Default Channel:** {get_setting('DEFAULT_CHANNEL_HANDLE', '@TheNewsForum')}")

st.divider()

st.subheader("💾 Database")
st.write(f"**DB Path:** {get_setting('DB_PATH', 'data/ytseo.sqlite')}")

st.divider()

st.subheader("🤖 LLM Configuration")
st.write(f"**Provider:** {get_setting('LLM_PROVIDER', 'ollama')}")
st.write(f"**Model:** {get_setting('MODEL_NAME', 'llama3.1')}")
st.write(f"**Ollama URL:** {get_setting('OLLAMA_BASE_URL', 'http://localhost:11434')}")

st.divider()

st.subheader("🔒 Safety Controls")
st.write(f"**DRY_RUN:** {get_setting('DRY_RUN', 'true')}")
st.write(f"**REQUIRE_CONFIRMATION:** {get_setting('REQUIRE_CONFIRMATION', 'true')}")
st.write(f"**MERGE_TAGS:** {get_setting('MERGE_TAGS', 'true')}")

st.divider()

st.subheader("🎨 UI Configuration")
st.write(f"**Streamlit Port:** {get_setting('STREAMLIT_PORT', 8502)}")
