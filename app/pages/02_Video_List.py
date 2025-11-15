import streamlit as st
import sqlite3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from ytseo import workflows

st.title("📹 Video List")

# Fetch Video Section
with st.expander("🎯 Fetch Specific Video from YouTube", expanded=False):
    st.write("Enter a YouTube video ID to fetch and process immediately.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        video_id_input = st.text_input(
            "YouTube Video ID",
            placeholder="e.g., 1MvFqJqq4IA (from youtube.com/watch?v=...)",
            help="Get this from the YouTube URL: youtube.com/watch?v=VIDEO_ID"
        )
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        fetch_button = st.button("🚀 Fetch & Process", type="primary")
    
    if fetch_button:
        if not video_id_input or len(video_id_input) < 5:
            st.error("Please enter a valid YouTube video ID")
        else:
            with st.spinner(f"Fetching video {video_id_input} from YouTube..."):
                try:
                    result = workflows.fetch_and_process_video(video_id_input)
                    if result:
                        st.success(f"✅ Video fetched and processed! Check Video Detail page.")
                        st.rerun()
                    else:
                        st.error("❌ Failed to fetch video. Check the video ID and try again.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

st.divider()

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
