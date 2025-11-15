from __future__ import annotations

from typing import Dict, List

from . import db as dbmod
from . import models
from . import seo_engine
from . import youtube_api


def sync_channel(channel_handle: str, limit: int = 20) -> int:
    """Sync videos from YouTube channel to local database."""
    conn = dbmod.connect()
    dbmod.apply_migrations(conn)
    videos = youtube_api.list_videos_by_channel(channel_handle, limit=limit)
    for v in videos:
        models.upsert_video(
            conn,
            video_id=v.get("video_id"),
            channel_id=v.get("channel_id"),
            title_original=v.get("title_original"),
            description_original=v.get("description_original"),
            tags_original=v.get("tags_original"),
            published_at=v.get("published_at"),
            episode_id=v.get("episode_id"),
            status=v.get("status", "pending"),
        )
    return len(videos)


def generate_suggestions_for_video(video_id: str, language_code: str = "en") -> int:
    """
    Generate SEO suggestions for a specific video by ID.
    Useful for targeted regeneration or processing a single video.
    """
    conn = dbmod.connect()
    dbmod.apply_migrations(conn)
    
    # Fetch the specific video
    cur = conn.execute("SELECT * FROM yt_videos WHERE video_id=?", (video_id,))
    row = cur.fetchone()
    
    if not row:
        print(f"Video {video_id} not found in database")
        return 0
    
    v = dict(row)
    
    # Build context with video data
    ctx = dict(v)
    
    # Generate all SEO fields
    suggestion = {
        "title": seo_engine.generate_title(ctx),
        "description": seo_engine.generate_description(ctx),
        "tags": seo_engine.generate_tags(ctx),
        "hashtags": seo_engine.generate_hashtags(ctx),
        "thumbnail_text": seo_engine.generate_thumbnail_text(ctx),
        "pinned_comment": seo_engine.generate_pinned_comment(ctx),
    }
    
    # Store suggestion
    models.create_suggestion(
        conn,
        video_id=v["video_id"],
        language_code=language_code,
        title=suggestion["title"],
        description=suggestion["description"],
        tags=suggestion["tags"],
        hashtags=suggestion["hashtags"],
        thumbnail_text="\n".join(suggestion["thumbnail_text"]),
        pinned_comment=suggestion["pinned_comment"],
        playlists=[],
    )
    
    # Update video status to 'suggested'
    conn.execute("UPDATE yt_videos SET status='suggested' WHERE video_id=?", (v["video_id"],))
    conn.commit()
    
    print(f"Generated suggestion for video: {v['video_id']} - {v['title_original'][:50]}...")
    return 1


def generate_suggestions(limit: int = 10, language_code: str = "en", priority: str = "recent") -> int:
    """
    Generate SEO suggestions for pending videos using LLM.
    Context is enriched with AI-EWG episode data if episode_id is set.
    
    Priority modes:
    - 'recent': Process newest videos first (default)
    - 'oldest': Process oldest videos first
    - 'popular': Process by view count (requires analytics data)
    - 'linked': Process videos with episode_id first (AI-EWG linked)
    """
    conn = dbmod.connect()
    dbmod.apply_migrations(conn)
    
    # Build query based on priority
    if priority == "recent":
        order_by = "published_at DESC"
    elif priority == "oldest":
        order_by = "published_at ASC"
    elif priority == "linked":
        # Prioritize videos with episode_id, then by date
        order_by = "(episode_id IS NOT NULL) DESC, published_at DESC"
    else:
        order_by = "published_at DESC"
    
    query = f"SELECT * FROM yt_videos WHERE status='pending' ORDER BY {order_by} LIMIT ?"
    vids = [dict(row) for row in conn.execute(query, (limit,)).fetchall()]
    created = 0
    
    for v in vids:
        # Build context with video data
        ctx = dict(v)
        
        # Generate all SEO fields
        suggestion = {
            "title": seo_engine.generate_title(ctx),
            "description": seo_engine.generate_description(ctx),
            "tags": seo_engine.generate_tags(ctx),
            "hashtags": seo_engine.generate_hashtags(ctx),
            "thumbnail_text": seo_engine.generate_thumbnail_text(ctx),
            "pinned_comment": seo_engine.generate_pinned_comment(ctx),
        }
        
        # Store suggestion
        models.create_suggestion(
            conn,
            video_id=v["video_id"],
            language_code=language_code,
            title=suggestion["title"],
            description=suggestion["description"],
            tags=suggestion["tags"],
            hashtags=suggestion["hashtags"],
            thumbnail_text=", ".join(suggestion["thumbnail_text"]) if isinstance(suggestion["thumbnail_text"], list) else suggestion["thumbnail_text"],
            pinned_comment=suggestion["pinned_comment"],
            playlists=[],
        )
        
        # Mark video as suggested
        models.mark_video_status(conn, v["video_id"], "suggested")
        created += 1
    
    return created


def apply_suggestions(limit: int = 10, dry_run: bool = True) -> int:
    """
    Apply approved suggestions to YouTube.
    Respects DRY_RUN and REQUIRE_CONFIRMATION settings.
    """
    conn = dbmod.connect()
    dbmod.apply_migrations(conn)
    vids = models.get_videos_by_status(conn, status="approved", limit=limit)
    applied = 0
    
    for v in vids:
        # Get latest suggestion for this video
        cur = conn.execute(
            "SELECT title, description, tags_json FROM yt_video_suggestions WHERE video_id=? ORDER BY created_at DESC LIMIT 1",
            (v["video_id"],)
        )
        suggestion = cur.fetchone()
        if not suggestion:
            continue
        
        import json
        changes = {
            "title": suggestion[0],
            "description": suggestion[1],
            "tags": json.loads(suggestion[2]) if suggestion[2] else []
        }
        
        # Apply to YouTube
        success = youtube_api.update_video_metadata(v["video_id"], changes, require_confirmation=not dry_run)
        
        if success:
            models.mark_video_status(conn, v["video_id"], "applied")
            applied += 1
    
    return applied
