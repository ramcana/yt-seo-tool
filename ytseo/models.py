from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List, Optional


def upsert_channel(conn: sqlite3.Connection, channel_id: str, title: str, last_synced: Optional[str] = None) -> None:
    conn.execute(
        """
        INSERT INTO yt_channels(channel_id, title, last_synced)
        VALUES(?, ?, ?)
        ON CONFLICT(channel_id) DO UPDATE SET
            title=excluded.title,
            last_synced=excluded.last_synced
        """,
        (channel_id, title, last_synced),
    )
    conn.commit()


def upsert_video(
    conn: sqlite3.Connection,
    video_id: str,
    channel_id: Optional[str] = None,
    channel_handle: Optional[str] = None,
    title_original: Optional[str] = None,
    description_original: Optional[str] = None,
    tags_original: Optional[List[str]] = None,
    published_at: Optional[str] = None,
    episode_id: Optional[str] = None,
    status: Optional[str] = None,
) -> None:
    tags_json = json.dumps(tags_original or [])
    
    # Check if channel_handle column exists (for backward compatibility)
    cursor = conn.execute("PRAGMA table_info(yt_videos)")
    columns = [row[1] for row in cursor.fetchall()]
    has_channel_handle = "channel_handle" in columns
    
    if has_channel_handle:
        conn.execute(
            """
            INSERT INTO yt_videos(video_id, channel_id, channel_handle, title_original, description_original, tags_original, published_at, episode_id, status)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(video_id) DO UPDATE SET
                channel_id=excluded.channel_id,
                channel_handle=excluded.channel_handle,
                title_original=excluded.title_original,
                description_original=excluded.description_original,
                tags_original=excluded.tags_original,
                published_at=excluded.published_at,
                episode_id=excluded.episode_id,
                status=excluded.status
            """,
            (video_id, channel_id, channel_handle, title_original, description_original, tags_json, published_at, episode_id, status),
        )
    else:
        # Fallback for old schema without channel_handle
        conn.execute(
            """
            INSERT INTO yt_videos(video_id, channel_id, title_original, description_original, tags_original, published_at, episode_id, status)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(video_id) DO UPDATE SET
                channel_id=excluded.channel_id,
                title_original=excluded.title_original,
                description_original=excluded.description_original,
                tags_original=excluded.tags_original,
                published_at=excluded.published_at,
                episode_id=excluded.episode_id,
                status=excluded.status
            """,
            (video_id, channel_id, title_original, description_original, tags_json, published_at, episode_id, status),
        )
    conn.commit()


def create_suggestion(
    conn: sqlite3.Connection,
    video_id: str,
    language_code: str,
    title: str,
    description: str,
    tags: List[str],
    hashtags: List[str],
    thumbnail_text: str,
    pinned_comment: str,
    playlists: List[str],
) -> int:
    cur = conn.execute(
        """
        INSERT INTO yt_video_suggestions(
            video_id, language_code, title, description, tags_json, hashtags_json, thumbnail_text, pinned_comment, playlists_json, created_at
        ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (
            video_id,
            language_code,
            title,
            description,
            json.dumps(tags),
            json.dumps(hashtags),
            thumbnail_text,
            pinned_comment,
            json.dumps(playlists),
        ),
    )
    conn.commit()
    return int(cur.lastrowid)


def mark_video_status(conn: sqlite3.Connection, video_id: str, status: str) -> None:
    conn.execute("UPDATE yt_videos SET status=? WHERE video_id=?", (status, video_id))
    conn.commit()


def get_videos_by_status(conn: sqlite3.Connection, status: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    # Emulate NULLS LAST in SQLite by sorting on (published_at IS NULL) first
    if status:
        cur = conn.execute(
            "SELECT * FROM yt_videos WHERE status=? ORDER BY (published_at IS NULL), published_at DESC LIMIT ?",
            (status, limit),
        )
    else:
        cur = conn.execute(
            "SELECT * FROM yt_videos ORDER BY (published_at IS NULL), published_at DESC LIMIT ?",
            (limit,),
        )
    rows = cur.fetchall()
    return [dict(r) for r in rows]


def get_counts_by_status(conn: sqlite3.Connection) -> Dict[str, int]:
    cur = conn.execute("SELECT status, COUNT(*) as c FROM yt_videos GROUP BY status")
    out: Dict[str, int] = {}
    for r in cur.fetchall():
        if r[0] is not None:
            out[str(r[0])] = int(r[1])
    return out
