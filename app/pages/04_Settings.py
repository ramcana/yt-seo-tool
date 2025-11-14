import os
import streamlit as st

try:
    from ytseo.config import get_setting
except Exception:
    def get_setting(key: str, default=None):
        return os.environ.get(key, default)

st.title("Settings")
st.write(f"DB_PATH: {get_setting('DB_PATH', 'data/ytseo.sqlite')}")
st.write(f"DEFAULT_CHANNEL_HANDLE: {get_setting('DEFAULT_CHANNEL_HANDLE', '@TheNewsForum')}")
st.write(f"STREAMLIT_PORT: {get_setting('STREAMLIT_PORT', 8502)}")
