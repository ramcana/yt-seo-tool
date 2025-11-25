import streamlit as st
import sqlite3
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import render_channel_selector

# Render channel selector
selected_channel = render_channel_selector()

st.title("📊 Dashboard")
st.caption(f"Viewing data for: **{selected_channel}**")

# Connect to database
db_path = Path("data/ytseo.sqlite")
if not db_path.exists():
    st.warning("Database not found. Run `ytseo sync` first.")
    st.stop()

conn = sqlite3.connect(str(db_path))

# Get channel ID for filtering
channel_id_result = conn.execute(
    "SELECT DISTINCT channel_id FROM yt_videos WHERE channel_id IN (SELECT channel_id FROM yt_videos) LIMIT 1"
).fetchone()

# Get counts by status (optionally filtered by channel if we have channel data)
status_counts = {}
for status in ['pending', 'suggested', 'approved', 'applied']:
    # For now, show all videos regardless of channel
    # TODO: Add channel_handle column to yt_videos table for proper filtering
    count = conn.execute("SELECT COUNT(*) FROM yt_videos WHERE status=?", (status,)).fetchone()[0]
    status_counts[status] = count

# Display metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("⏳ Pending", status_counts['pending'])
with col2:
    st.metric("✨ Suggested", status_counts['suggested'])
with col3:
    st.metric("✅ Approved", status_counts['approved'])
with col4:
    st.metric("🚀 Applied", status_counts['applied'])

st.divider()

# Daily target
st.subheader("Daily Target")
daily_target = 10
optimized_today = status_counts['approved'] + status_counts['applied']
remaining = max(0, daily_target - optimized_today)

progress = min(1.0, optimized_today / daily_target)
st.progress(progress)
st.write(f"**{optimized_today} / {daily_target}** videos optimized")
if remaining > 0:
    st.info(f"📌 {remaining} more videos to reach daily target")
else:
    st.success("🎉 Daily target reached!")

st.divider()

# Recent activity
st.subheader("Recent Activity")
recent = conn.execute(
    "SELECT video_id, title_original, status, published_at FROM yt_videos ORDER BY ROWID DESC LIMIT 5"
).fetchall()

for video in recent:
    status_emoji = {"pending": "⏳", "suggested": "✨", "approved": "✅", "applied": "🚀"}.get(video[2], "")
    st.write(f"{status_emoji} **{video[1][:60]}...** ({video[2]})")

conn.close()
