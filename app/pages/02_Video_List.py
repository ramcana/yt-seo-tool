import streamlit as st
import sqlite3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from ytseo import workflows
from shared import render_channel_selector

# Render channel selector
selected_channel = render_channel_selector()

st.title("📹 Video List")
st.caption(f"Viewing videos for: **{selected_channel}**")

# Sync Channel Section
with st.expander("🔄 Sync Channel from YouTube", expanded=False):
    st.write(f"Fetch latest videos from **{selected_channel}**")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        sync_limit = st.number_input(
            "Number of videos to sync",
            min_value=5,
            max_value=50,
            value=20,
            help="Fetch the most recent N videos from the channel"
        )
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        sync_button = st.button("🔄 Sync Channel", type="primary")
    
    if sync_button:
        with st.spinner(f"Syncing {sync_limit} videos from {selected_channel}..."):
            try:
                count = workflows.sync_channel(selected_channel, limit=sync_limit)
                st.success(f"✅ Synced {count} videos from {selected_channel}!")
                st.rerun()
            except Exception as e:
                st.error(f"Error syncing channel: {str(e)}")

# Generate SEO Section
with st.expander("✨ Generate SEO Suggestions", expanded=False):
    st.write("Generate AI-powered SEO suggestions for pending videos")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        gen_limit = st.number_input(
            "Number of videos",
            min_value=1,
            max_value=50,
            value=10,
            key="gen_limit",
            help="Process this many pending videos"
        )
    with col2:
        gen_priority = st.selectbox(
            "Priority",
            ["recent", "oldest", "linked"],
            help="recent: newest first, oldest: oldest first, linked: AI-EWG linked first"
        )
    with col3:
        st.write("")  # Spacing
        st.write("")  # Spacing
        gen_button = st.button("✨ Generate", type="primary", key="gen_btn")
    
    if gen_button:
        with st.spinner(f"Generating SEO suggestions for {gen_limit} videos..."):
            try:
                count = workflows.generate_suggestions(limit=gen_limit, priority=gen_priority)
                st.success(f"✅ Generated suggestions for {count} videos!")
                st.rerun()
            except Exception as e:
                st.error(f"Error generating suggestions: {str(e)}")

# Apply Changes Section
with st.expander("🚀 Apply Approved Changes", expanded=False):
    st.write("Apply approved SEO suggestions to YouTube")
    st.warning("⚠️ This will update videos on YouTube. Make sure DRY_RUN is enabled for testing!")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        apply_limit = st.number_input(
            "Number of videos to apply",
            min_value=1,
            max_value=20,
            value=5,
            key="apply_limit",
            help="Apply changes to this many approved videos"
        )
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        apply_button = st.button("🚀 Apply Changes", type="secondary", key="apply_btn")
    
    if apply_button:
        with st.spinner(f"Applying changes to {apply_limit} videos..."):
            try:
                from ytseo.config import get_setting
                dry_run = get_setting("DRY_RUN", "true").lower() in ("true", "1", "yes")
                
                if dry_run:
                    st.info("🔒 DRY_RUN mode enabled - changes will be logged but not applied")
                
                count = workflows.apply_suggestions(limit=apply_limit, dry_run=dry_run)
                
                if dry_run:
                    st.success(f"✅ [DRY RUN] Would apply changes to {count} videos")
                else:
                    st.success(f"✅ Applied changes to {count} videos!")
                st.rerun()
            except Exception as e:
                st.error(f"Error applying changes: {str(e)}")

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
        action_cols = st.columns(4)
        
        with action_cols[0]:
            if st.button("👁️ View", key=f"view_{video['video_id']}", use_container_width=True):
                st.session_state.selected_video_id = video['video_id']
                st.switch_page("pages/03_Video_Detail.py")
        
        with action_cols[1]:
            if video['status'] == 'pending':
                if st.button("✨ Generate", key=f"gen_{video['video_id']}", use_container_width=True):
                    with st.spinner("Generating..."):
                        try:
                            workflows.generate_suggestions_for_video(video['video_id'])
                            st.success("✅ Generated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        with action_cols[2]:
            if video['status'] == 'suggested':
                if st.button("✅ Approve", key=f"approve_{video['video_id']}", use_container_width=True):
                    conn.execute("UPDATE yt_videos SET status='approved' WHERE video_id=?", (video['video_id'],))
                    conn.commit()
                    st.success("✅ Approved!")
                    st.rerun()
        
        with action_cols[3]:
            if video['status'] == 'approved':
                if st.button("🚀 Apply", key=f"apply_{video['video_id']}", use_container_width=True):
                    with st.spinner("Applying..."):
                        try:
                            from ytseo.config import get_setting
                            dry_run = get_setting("DRY_RUN", "true").lower() in ("true", "1", "yes")
                            workflows.apply_suggestions(limit=1, dry_run=dry_run)
                            st.success("✅ Applied!" if not dry_run else "✅ [DRY RUN] Logged!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

conn.close()
