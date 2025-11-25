import streamlit as st
import sqlite3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from ytseo import workflows
from ytseo.config import get_setting
from shared import render_channel_selector

# Render channel selector
selected_channel = render_channel_selector()

st.title("⚡ Bulk Actions")
st.caption(f"Perform batch operations on videos from: **{selected_channel}**")

# Connect to database
db_path = Path("data/ytseo.sqlite")
if not db_path.exists():
    st.warning("Database not found. Run sync first.")
    st.stop()

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

# Get counts
pending_count = conn.execute("SELECT COUNT(*) FROM yt_videos WHERE status='pending'").fetchone()[0]
suggested_count = conn.execute("SELECT COUNT(*) FROM yt_videos WHERE status='suggested'").fetchone()[0]
approved_count = conn.execute("SELECT COUNT(*) FROM yt_videos WHERE status='approved'").fetchone()[0]

# Display current state
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("⏳ Pending", pending_count)
with col2:
    st.metric("✨ Suggested", suggested_count)
with col3:
    st.metric("✅ Approved", approved_count)

st.divider()

# === GENERATE SUGGESTIONS ===
st.subheader("✨ Generate SEO Suggestions")
st.write(f"Generate AI-powered SEO suggestions for **{pending_count}** pending videos")

col1, col2 = st.columns(2)
with col1:
    gen_limit = st.number_input(
        "Number of videos to process",
        min_value=1,
        max_value=100,
        value=min(10, pending_count) if pending_count > 0 else 10,
        key="bulk_gen_limit"
    )
    
    gen_priority = st.selectbox(
        "Processing priority",
        ["recent", "oldest", "linked"],
        help="recent: newest first, oldest: oldest first, linked: AI-EWG linked first"
    )

with col2:
    st.write("")
    st.write("")
    st.write("")
    if st.button("✨ Generate Suggestions", type="primary", use_container_width=True, disabled=pending_count == 0):
        with st.spinner(f"Generating suggestions for {gen_limit} videos..."):
            try:
                count = workflows.generate_suggestions(limit=gen_limit, priority=gen_priority)
                st.success(f"✅ Generated suggestions for {count} videos!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.divider()

# === BULK APPROVE ===
st.subheader("✅ Bulk Approve Suggestions")
st.write(f"Approve **{suggested_count}** suggested videos at once")

col1, col2 = st.columns(2)
with col1:
    approve_limit = st.number_input(
        "Number of videos to approve",
        min_value=1,
        max_value=100,
        value=min(10, suggested_count) if suggested_count > 0 else 10,
        key="bulk_approve_limit"
    )

with col2:
    st.write("")
    st.write("")
    st.write("")
    if st.button("✅ Bulk Approve", type="primary", use_container_width=True, disabled=suggested_count == 0):
        with st.spinner(f"Approving {approve_limit} videos..."):
            try:
                conn.execute(
                    "UPDATE yt_videos SET status='approved' WHERE video_id IN (SELECT video_id FROM yt_videos WHERE status='suggested' LIMIT ?)",
                    (approve_limit,)
                )
                conn.commit()
                st.success(f"✅ Approved {approve_limit} videos!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.divider()

# === APPLY TO YOUTUBE ===
st.subheader("🚀 Apply Changes to YouTube")
st.write(f"Apply **{approved_count}** approved suggestions to YouTube")

dry_run = get_setting("DRY_RUN", "true").lower() in ("true", "1", "yes")

if dry_run:
    st.info("🔒 **DRY_RUN mode is ENABLED** - Changes will be logged but NOT applied to YouTube")
else:
    st.error("⚠️ **DRY_RUN mode is DISABLED** - Changes WILL be applied to YouTube!")

col1, col2 = st.columns(2)
with col1:
    apply_limit = st.number_input(
        "Number of videos to apply",
        min_value=1,
        max_value=20,
        value=min(5, approved_count) if approved_count > 0 else 5,
        key="bulk_apply_limit"
    )
    
    st.caption("⚠️ Start with small batches (5-10) to test")

with col2:
    st.write("")
    st.write("")
    st.write("")
    if st.button("🚀 Apply to YouTube", type="secondary", use_container_width=True, disabled=approved_count == 0):
        with st.spinner(f"Applying changes to {apply_limit} videos..."):
            try:
                count = workflows.apply_suggestions(limit=apply_limit, dry_run=dry_run)
                
                if dry_run:
                    st.success(f"✅ [DRY RUN] Would apply changes to {count} videos")
                    st.info("💡 Set DRY_RUN=false in .env to actually apply changes")
                else:
                    st.success(f"✅ Applied changes to {count} videos on YouTube!")
                    st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.divider()

# === RESET/CLEANUP ===
st.subheader("🔄 Reset & Cleanup")

col1, col2 = st.columns(2)

with col1:
    st.write("**Reset videos to pending**")
    st.caption("Useful for regenerating suggestions")
    
    reset_status = st.selectbox(
        "Reset videos with status",
        ["suggested", "approved"],
        key="reset_status"
    )
    
    if st.button("🔄 Reset to Pending", use_container_width=True):
        count = conn.execute(
            "UPDATE yt_videos SET status='pending' WHERE status=?",
            (reset_status,)
        ).rowcount
        conn.commit()
        st.success(f"✅ Reset {count} videos to pending")
        st.rerun()

with col2:
    st.write("**Delete old suggestions**")
    st.caption("Clean up suggestion history")
    
    if st.button("🗑️ Delete All Suggestions", use_container_width=True):
        count = conn.execute("DELETE FROM yt_video_suggestions").rowcount
        conn.commit()
        st.success(f"✅ Deleted {count} suggestions")
        st.rerun()

conn.close()

st.divider()

# === WORKFLOW GUIDE ===
with st.expander("📖 Workflow Guide"):
    st.markdown("""
    ### Complete SEO Optimization Workflow
    
    1. **Sync Channel** (Video List page)
       - Fetch latest videos from YouTube
       - Videos start with `pending` status
    
    2. **Generate Suggestions** (This page or Video List)
       - AI generates SEO metadata for pending videos
       - Status changes to `suggested`
    
    3. **Review & Approve** (Video Detail page)
       - Review suggestions side-by-side with originals
       - Approve good suggestions
       - Reject or regenerate if needed
       - Status changes to `approved`
    
    4. **Apply to YouTube** (This page)
       - Apply approved changes to YouTube
       - Test with DRY_RUN=true first!
       - Status changes to `applied`
    
    ### Tips
    - Start with small batches (5-10 videos)
    - Always test with DRY_RUN enabled first
    - Review at least a few suggestions manually before bulk approval
    - Use priority="linked" for videos with AI-EWG episode data
    """)
