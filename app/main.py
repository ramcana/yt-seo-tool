import streamlit as st
from shared import render_channel_selector

st.set_page_config(page_title="YT SEO Tool", layout="wide")

# Render channel selector in sidebar
selected_channel = render_channel_selector()

st.title("YT SEO Tool")
st.write("Use the sidebar to navigate the pages. This is the main entrypoint.")
st.info(f"📺 Active Channel: **{selected_channel}**")
