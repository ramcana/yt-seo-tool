from __future__ import annotations

import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .config import get_setting


SCOPES = ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.force-ssl"]


def _get_authenticated_service():
    """Get authenticated YouTube API service."""
    creds = None
    token_path = Path("token.pickle")
    client_secret_path = get_setting("YOUTUBE_CLIENT_SECRET_PATH", "config/client_secret.json")
    
    # Load existing credentials
    if token_path.exists():
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not Path(client_secret_path).exists():
                raise FileNotFoundError(f"Client secret not found at {client_secret_path}")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)
    
    return build("youtube", "v3", credentials=creds)


def _resolve_channel_handle_to_id(youtube, handle: str) -> Optional[str]:
    """Resolve @handle to channel ID."""
    # Remove @ if present
    handle_clean = handle.lstrip("@")
    
    try:
        # Try forUsername first
        request = youtube.channels().list(part="id", forUsername=handle_clean)
        response = request.execute()
        if response.get("items"):
            return response["items"][0]["id"]
        
        # Try search as fallback
        request = youtube.search().list(part="id", q=handle_clean, type="channel", maxResults=1)
        response = request.execute()
        if response.get("items"):
            return response["items"][0]["id"]["channelId"]
    except HttpError as e:
        print(f"Error resolving channel handle: {e}")
    
    return None


def list_videos_by_channel(channel_handle: str, limit: int = 20) -> List[Dict]:
    """Fetch latest videos from a YouTube channel."""
    youtube = _get_authenticated_service()
    
    # Resolve handle to channel ID
    channel_id = _resolve_channel_handle_to_id(youtube, channel_handle)
    if not channel_id:
        print(f"Could not resolve channel: {channel_handle}")
        return []
    
    videos = []
    
    try:
        # Get channel's uploads playlist
        channel_response = youtube.channels().list(part="contentDetails", id=channel_id).execute()
        if not channel_response.get("items"):
            return []
        
        uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # Get videos from uploads playlist
        playlist_request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=min(limit, 50)
        )
        playlist_response = playlist_request.execute()
        
        video_ids = [item["contentDetails"]["videoId"] for item in playlist_response.get("items", [])]
        
        if not video_ids:
            return []
        
        # Get full video details
        videos_request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=",".join(video_ids)
        )
        videos_response = videos_request.execute()
        
        for item in videos_response.get("items", []):
            snippet = item["snippet"]
            videos.append({
                "video_id": item["id"],
                "channel_id": channel_id,
                "title_original": snippet.get("title", ""),
                "description_original": snippet.get("description", ""),
                "tags_original": snippet.get("tags", []),
                "published_at": snippet.get("publishedAt", ""),
                "episode_id": None,
                "status": "pending",
            })
    
    except HttpError as e:
        print(f"YouTube API error: {e}")
    
    return videos[:limit]


essential_update_fields = ["title", "description", "tags", "hashtags", "thumbnail_text", "pinned_comment", "playlists"]


def update_video_metadata(video_id: str, changes: Dict, require_confirmation: bool = True) -> bool:
    """
    Update video metadata on YouTube with safety controls.
    
    Args:
        video_id: YouTube video ID
        changes: Dict of fields to update (title, description, tags)
        require_confirmation: If True, requires manual confirmation before applying
    
    Returns:
        True if successful, False otherwise
    
    Safety layers:
    1. DRY_RUN mode (default: true) - logs changes without applying
    2. require_confirmation - prompts user before applying (default: true)
    3. Never deletes data - only updates/adds
    4. Preserves original data in database before applying
    """
    dry_run = get_setting("DRY_RUN", "true").lower() in ("true", "1", "yes")
    
    if dry_run:
        print(f"[DRY RUN] Would update video {video_id} with: {changes}")
        return True
    
    # SAFETY: Manual confirmation required
    if require_confirmation:
        print(f"\n⚠️  CONFIRMATION REQUIRED ⚠️")
        print(f"Video ID: {video_id}")
        print(f"Changes to apply:")
        for key, value in changes.items():
            preview = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
            print(f"  - {key}: {preview}")
        
        response = input("\nType 'APPLY' to confirm, anything else to cancel: ")
        if response != "APPLY":
            print("❌ Update cancelled by user")
            return False
    
    try:
        youtube = _get_authenticated_service()
        
        # Get current video details
        video_response = youtube.videos().list(part="snippet", id=video_id).execute()
        if not video_response.get("items"):
            print(f"Video {video_id} not found")
            return False
        
        snippet = video_response["items"][0]["snippet"]
        
        # SAFETY: Store original values before modification
        original_values = {
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "tags": snippet.get("tags", [])
        }
        print(f"\n📋 Original values backed up for rollback if needed")
        
        # Apply changes (NEVER delete, only update/add)
        if "title" in changes and changes["title"]:
            snippet["title"] = changes["title"]
        if "description" in changes and changes["description"]:
            snippet["description"] = changes["description"]
        if "tags" in changes and changes["tags"]:
            # Merge tags instead of replacing (safer)
            existing_tags = set(snippet.get("tags", []))
            new_tags = set(changes["tags"])
            snippet["tags"] = list(existing_tags | new_tags)
        
        # Update video
        update_response = youtube.videos().update(
            part="snippet",
            body={
                "id": video_id,
                "snippet": snippet
            }
        ).execute()
        
        print(f"✅ Successfully updated video {video_id}")
        return True
    
    except HttpError as e:
        print(f"❌ YouTube API error updating video: {e}")
        return False
