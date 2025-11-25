import streamlit as st
import sqlite3
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import render_channel_selector

# Render channel selector
selected_channel = render_channel_selector()

st.title("🎬 Video Detail")

# Connect to database
db_path = Path("data/ytseo.sqlite")
if not db_path.exists():
    st.warning("Database not found. Run `ytseo sync` first.")
    st.stop()

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

# Video selector
videos = conn.execute("SELECT video_id, title_original, status FROM yt_videos ORDER BY published_at DESC LIMIT 50").fetchall()
video_options = {f"{v['title_original'][:60]}... ({v['status']})": v['video_id'] for v in videos}

if not video_options:
    st.warning("No videos found. Run `ytseo sync` first.")
    st.stop()

selected_title = st.selectbox("Select Video", list(video_options.keys()))
video_id = video_options[selected_title]

# Fetch video details
video = conn.execute("SELECT * FROM yt_videos WHERE video_id=?", (video_id,)).fetchone()

if not video:
    st.error("Video not found")
    st.stop()

# Display video info
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader(video['title_original'])
    st.write(f"**Video ID:** `{video['video_id']}`")
    st.write(f"**Published:** {video['published_at']}")
    st.write(f"**Channel:** {video['channel_id']}")
with col2:
    status_emoji = {"pending": "⏳", "suggested": "✨", "approved": "✅", "applied": "🚀"}.get(video['status'], "")
    st.metric("Status", f"{status_emoji} {video['status']}")

st.divider()

# Language selector (for future multi-language support)
language = st.selectbox("Language", ["en (English)", "fr (French)"], index=0)
language_code = language.split()[0]

# Fetch suggestions
suggestions = conn.execute(
    "SELECT * FROM yt_video_suggestions WHERE video_id=? AND language_code=? ORDER BY created_at DESC",
    (video_id, language_code)
).fetchall()

if not suggestions:
    st.info("No suggestions generated yet. Run `ytseo generate` to create suggestions.")
    
    # Show original metadata only
    st.subheader("📄 Original Metadata")
    
    with st.expander("Title", expanded=True):
        st.write(video['title_original'] or "_No title_")
    
    with st.expander("Description", expanded=True):
        st.write(video['description_original'] or "_No description_")
    
    with st.expander("Tags", expanded=True):
        tags = json.loads(video['tags_original']) if video['tags_original'] else []
        st.write(", ".join(tags) if tags else "_No tags_")
    
    conn.close()
    st.stop()

# Get latest suggestion
suggestion = suggestions[0]

# Side-by-side comparison
st.subheader("📊 Original vs Suggested")

# Title comparison
st.markdown("### 📝 Title")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Original**")
    st.info(video['title_original'] or "_No title_")
with col2:
    st.markdown("**Suggested**")
    st.success(suggestion['title'] or "_No suggestion_")

# Description comparison
st.markdown("### 📄 Description")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Original**")
    with st.expander("View full description"):
        st.write(video['description_original'] or "_No description_")
with col2:
    st.markdown("**Suggested**")
    with st.expander("View full description"):
        st.write(suggestion['description'] or "_No suggestion_")

# Tags comparison
st.markdown("### 🏷️ Tags")
col1, col2 = st.columns(2)

original_tags = json.loads(video['tags_original']) if video['tags_original'] else []
suggested_tags = json.loads(suggestion['tags_json']) if suggestion['tags_json'] else []

with col1:
    st.markdown("**Original**")
    st.write(f"**Count:** {len(original_tags)}")
    if original_tags:
        st.write(", ".join(original_tags[:10]))
        if len(original_tags) > 10:
            with st.expander("View all tags"):
                st.write(", ".join(original_tags))
    else:
        st.write("_No tags_")

with col2:
    st.markdown("**Suggested**")
    st.write(f"**Count:** {len(suggested_tags)}")
    if suggested_tags:
        st.write(", ".join(suggested_tags[:10]))
        if len(suggested_tags) > 10:
            with st.expander("View all tags"):
                st.write(", ".join(suggested_tags))
    else:
        st.write("_No suggestions_")

# Hashtags
st.markdown("### #️⃣ Hashtags")
hashtags = json.loads(suggestion['hashtags_json']) if suggestion['hashtags_json'] else []
if hashtags:
    st.write(" ".join(hashtags))
else:
    st.write("_No hashtags_")

# Thumbnail text
st.markdown("### 🖼️ Thumbnail Text Options")
if suggestion['thumbnail_text']:
    options = suggestion['thumbnail_text'].split(", ")
    for i, opt in enumerate(options, 1):
        st.write(f"{i}. **{opt}**")
else:
    st.write("_No thumbnail text_")

# Pinned comment
st.markdown("### 💬 Pinned Comment")
if suggestion['pinned_comment']:
    st.info(suggestion['pinned_comment'])
else:
    st.write("_No pinned comment_")

st.divider()

# Actions
st.subheader("⚡ Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("✅ Approve", type="primary", use_container_width=True, disabled=video['status'] == 'approved'):
        conn.execute("UPDATE yt_videos SET status='approved' WHERE video_id=?", (video_id,))
        conn.commit()
        st.success("✅ Approved! Ready to apply.")
        st.rerun()

with col2:
    if st.button("🔄 Regenerate", use_container_width=True):
        # Mark as pending and regenerate immediately
        conn.execute("UPDATE yt_videos SET status='pending' WHERE video_id=?", (video_id,))
        conn.commit()
        
        with st.spinner("Regenerating suggestions..."):
            try:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent.parent))
                from ytseo import workflows
                workflows.generate_suggestions_for_video(video_id)
                st.success("🔄 Regenerated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

with col3:
    if st.button("❌ Reject", use_container_width=True):
        # Delete suggestion and mark as pending
        conn.execute("DELETE FROM yt_video_suggestions WHERE video_id=?", (video_id,))
        conn.execute("UPDATE yt_videos SET status='pending' WHERE video_id=?", (video_id,))
        conn.commit()
        st.warning("❌ Suggestion rejected.")
        st.rerun()

with col4:
    if st.button("🚀 Apply Now", type="secondary", use_container_width=True, disabled=video['status'] != 'approved'):
        with st.spinner("Applying to YouTube..."):
            try:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent.parent))
                from ytseo import workflows, config
                
                dry_run = config.get_setting("DRY_RUN", "true").lower() in ("true", "1", "yes")
                
                if dry_run:
                    st.info("🔒 DRY_RUN mode enabled")
                
                workflows.apply_suggestions(limit=1, dry_run=dry_run)
                
                if dry_run:
                    st.success("✅ [DRY RUN] Logged changes")
                else:
                    st.success("✅ Applied to YouTube!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Show suggestion history
if len(suggestions) > 1:
    st.divider()
    st.subheader("📜 Suggestion History")
    st.write(f"**{len(suggestions)} suggestions** generated for this video")
    
    for i, sug in enumerate(suggestions, 1):
        with st.expander(f"Suggestion #{i} - {sug['created_at']}"):
            st.write(f"**Title:** {sug['title']}")
            st.write(f"**Tags:** {len(json.loads(sug['tags_json']) if sug['tags_json'] else [])}")

conn.close()
