from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

from .config import get_setting


def _connect_ai_ewg() -> Optional[sqlite3.Connection]:
    """Connect to AI-EWG database (read-only)."""
    db_path = get_setting("AI_EWG_DB_PATH", "../ai-ewg/data/pipeline.db")
    p = Path(db_path)
    if not p.exists():
        return None
    conn = sqlite3.connect(f"file:{p.absolute()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def get_episode_by_id(episode_id: str) -> Optional[Dict]:
    """
    Fetch episode from AI-EWG by episode_id.
    
    Returns dict with:
    - id, title, summary, topics, guest_names, duration_seconds, metadata (JSON)
    """
    conn = _connect_ai_ewg()
    if not conn:
        return None
    
    try:
        # Get from json_metadata_index for quick access
        cur = conn.execute(
            """
            SELECT 
                episode_id, title, duration_seconds, 
                show_name, date, guest_names, topics,
                has_transcript, has_enrichment, has_editorial
            FROM json_metadata_index
            WHERE episode_id = ?
            """,
            (episode_id,)
        )
        row = cur.fetchone()
        if not row:
            return None
        
        result = dict(row)
        
        # Parse JSON fields if they're strings
        if result.get("guest_names") and isinstance(result["guest_names"], str):
            try:
                result["guest_names"] = json.loads(result["guest_names"])
            except:
                result["guest_names"] = []
        
        if result.get("topics") and isinstance(result["topics"], str):
            try:
                result["topics"] = json.loads(result["topics"])
            except:
                result["topics"] = []
        
        # Try to get full metadata from episodes table
        cur = conn.execute("SELECT metadata FROM episodes WHERE id = ?", (episode_id,))
        meta_row = cur.fetchone()
        if meta_row and meta_row[0]:
            try:
                full_meta = json.loads(meta_row[0])
                result["full_metadata"] = full_meta
                
                # Extract enrichment data if available
                if "enrichment" in full_meta and full_meta["enrichment"]:
                    enrich = full_meta["enrichment"]
                    result["summary"] = enrich.get("summary", "")
                    result["entities"] = enrich.get("entities", [])
                    result["key_moments"] = enrich.get("key_moments", [])
            except:
                pass
        
        return result
    finally:
        conn.close()


def get_episode_for_youtube_video(video_id: str) -> Optional[Dict]:
    """
    Map YouTube video_id to AI-EWG episode (stub for now).
    
    TODO: Implement mapping logic:
    - Check yt_videos.episode_id field
    - Or match by title/date heuristics
    """
    # For now, this is a stub - will be implemented in Phase 9
    return None


def search_episodes_by_title(title: str, limit: int = 5) -> List[Dict]:
    """Search AI-EWG episodes by title (for manual mapping UI)."""
    conn = _connect_ai_ewg()
    if not conn:
        return []
    
    try:
        cur = conn.execute(
            """
            SELECT episode_id, title, show_name, date, guest_names
            FROM json_metadata_index
            WHERE title LIKE ?
            ORDER BY date DESC
            LIMIT ?
            """,
            (f"%{title}%", limit)
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
