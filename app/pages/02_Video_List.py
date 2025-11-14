import streamlit as st
import sqlite3
from pathlib import Path

st.title("📹 Video List")

# Connect to database
db_path = Path("data/ytseo.sqlite")
if not db_path.exists():
    st.warning("Database not found. Run `ytseo sync` first.")
    st.stop()

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

# Filters
col1, col2 = st.columns(2)
with col1:
    status_filter = st.selectbox(
        "Filter by status",
        ["All", "pending", "suggested", "approved", "applied"]
    )
with col2:
    limit = st.number_input("Limit", min_value=5, max_value=100, value=20)

# Query videos
if status_filter == "All":
    query = "SELECT * FROM yt_videos ORDER BY published_at DESC LIMIT ?"
    params = (limit,)
else:
    query = "SELECT * FROM yt_videos WHERE status=? ORDER BY published_at DESC LIMIT ?"
    params = (status_filter, limit)

videos = conn.execute(query, params).fetchall()

# Display videos
st.write(f"**{len(videos)} videos**")

for video in videos:
    with st.expander(f"🎬 {video['title_original'][:80]}..."):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**Video ID:** `{video['video_id']}`")
            st.write(f"**Published:** {video['published_at']}")
            st.write(f"**Status:** `{video['status']}`")
            
            # Check for suggestions
            suggestions = conn.execute(
                "SELECT COUNT(*) as count FROM yt_video_suggestions WHERE video_id=?",
                (video['video_id'],)
            ).fetchone()
            st.write(f"**Suggestions:** {suggestions['count']}")
        
        with col2:
            if video['status'] == 'pending':
                st.info("⏳ Pending")
            elif video['status'] == 'suggested':
                st.success("✨ Suggested")
            elif video['status'] == 'approved':
                st.warning("✅ Approved")
            elif video['status'] == 'applied':
                st.success("🚀 Applied")
        
        # Quick actions
        if st.button(f"View Details", key=f"view_{video['video_id']}"):
            st.switch_page("pages/03_Video_Detail.py")

conn.close()
