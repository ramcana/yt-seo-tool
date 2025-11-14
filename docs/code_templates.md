# yt-seo-tool – Initial Code Templates

This document contains initial code templates for key components of the `yt-seo-tool` repo.
You can copy these into the corresponding files when scaffolding the project.

---

## 1. `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "yt-seo-tool"
version = "0.1.0"
description = "YouTube SEO Refresh Tool for optimizing existing YouTube videos."
authors = [{ name = "Ramji Thiagarajan" }]
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
  "streamlit",
  "typer[all]",
  "google-api-python-client",
  "google-auth-httplib2",
  "google-auth-oauthlib",
  "python-dotenv",
  "toml",
  "yt-dlp"
]

[project.scripts]
ytseo = "cli.main:app"

[tool.setuptools.packages.find]
where = ["."]
```

---

## 2. `.gitignore`

```gitignore
__pycache__/
.pytest_cache/
.DS_Store
.env
*.sqlite3
*.db
credentials.json
token.json
.streamlit/
```

---

## 3. `config/settings.example.toml`

```toml
db_path = "yt_seo.db"
youtube_client_secret_path = "config/client_secret.json"
ai_ewg_db_path = "../ai-ewg/ai_ewg.db"
ai_ewg_http_url = "http://localhost:8000"
default_channel_handle = "@TheNewsForum"
streamlit_port = 8502
```

---

## 4. `.env.example`

```env
YTSEO_DB_PATH=yt_seo.db
YTSEO_YT_CLIENT_SECRET_PATH=config/client_secret.json
YTSEO_AI_EWG_DB_PATH=../ai-ewg/ai_ewg.db
YTSEO_AI_EWG_HTTP_URL=http://localhost:8000
YTSEO_DEFAULT_CHANNEL_HANDLE=@TheNewsForum
YTSEO_STREAMLIT_PORT=8502
```

---

## 5. `ytseo/config.py`

```python
import os
from dataclasses import dataclass
from typing import Optional

import toml
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    db_path: str
    youtube_client_secret_path: str
    ai_ewg_db_path: Optional[str]
    ai_ewg_http_url: Optional[str]
    default_channel_handle: str
    streamlit_port: int


def load_settings(config_path: str = "config/settings.toml") -> Settings:
    data = {}
    if os.path.exists(config_path):
        data = toml.load(config_path)

    db_path = os.getenv("YTSEO_DB_PATH", data.get("db_path", "yt_seo.db"))
    youtube_client_secret_path = os.getenv(
        "YTSEO_YT_CLIENT_SECRET_PATH",
        data.get("youtube_client_secret_path", "config/client_secret.json"),
    )
    ai_ewg_db_path = os.getenv(
        "YTSEO_AI_EWG_DB_PATH",
        data.get("ai_ewg_db_path", None),
    )
    ai_ewg_http_url = os.getenv(
        "YTSEO_AI_EWG_HTTP_URL",
        data.get("ai_ewg_http_url", None),
    )
    default_channel_handle = os.getenv(
        "YTSEO_DEFAULT_CHANNEL_HANDLE",
        data.get("default_channel_handle", "@TheNewsForum"),
    )
    streamlit_port = int(
        os.getenv("YTSEO_STREAMLIT_PORT", data.get("streamlit_port", 8502))
    )

    return Settings(
        db_path=db_path,
        youtube_client_secret_path=youtube_client_secret_path,
        ai_ewg_db_path=ai_ewg_db_path,
        ai_ewg_http_url=ai_ewg_http_url,
        default_channel_handle=default_channel_handle,
        streamlit_port=streamlit_port,
    )
```

---

## 6. `ytseo/db.py`

```python
import sqlite3
from pathlib import Path
from typing import Iterator, Optional

from .config import load_settings


_connection: Optional[sqlite3.Connection] = None


def get_connection() -> sqlite3.Connection:
    """Return a singleton SQLite connection, initializing DB and migrations if needed."""
    global _connection
    if _connection is not None:
        return _connection

    settings = load_settings()
    db_path = Path(settings.db_path)
    first_time = not db_path.exists()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    if first_time:
        run_migrations(conn)

    _connection = conn
    return conn


def run_migrations(conn: sqlite3.Connection) -> None:
    """Run initial migrations. Currently just executes 0001_init.sql."""
    migrations_dir = Path("migrations")
    init_sql = migrations_dir / "0001_init.sql"
    if init_sql.exists():
        with init_sql.open("r", encoding="utf-8") as f:
            sql = f.read()
        conn.executescript(sql)
        conn.commit()


def cursor() -> Iterator[sqlite3.Cursor]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
```

---

## 7. `migrations/0001_init.sql`

```sql
CREATE TABLE IF NOT EXISTS yt_channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id TEXT UNIQUE,
    title TEXT,
    last_synced TEXT
);

CREATE TABLE IF NOT EXISTS yt_videos (
    video_id TEXT PRIMARY KEY,
    channel_id TEXT,
    title_original TEXT,
    description_original TEXT,
    tags_original TEXT,
    published_at TEXT,
    episode_id TEXT,
    status TEXT
);

CREATE TABLE IF NOT EXISTS yt_video_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT,
    language_code TEXT,
    title TEXT,
    description TEXT,
    tags_json TEXT,
    hashtags_json TEXT,
    thumbnail_text TEXT,
    pinned_comment TEXT,
    playlists_json TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS yt_video_applied_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT,
    diff_json TEXT,
    applied_at TEXT
);

CREATE TABLE IF NOT EXISTS yt_language_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT,
    label TEXT,
    enabled INTEGER
);

CREATE TABLE IF NOT EXISTS yt_sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date TEXT,
    count_fetched INTEGER,
    notes TEXT
);
```

---

## 8. `ytseo/models.py`

```python
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .db import get_connection


def upsert_channel(channel_id: str, title: str) -> None:
    conn = get_connection()
    conn.execute(
        """INSERT INTO yt_channels (channel_id, title, last_synced)
               VALUES (?, ?, datetime('now'))
               ON CONFLICT(channel_id)
               DO UPDATE SET title=excluded.title,
                             last_synced=excluded.last_synced""",
        (channel_id, title),
    )
    conn.commit()


def upsert_video(
    video_id: str,
    channel_id: str,
    title_original: str,
    description_original: str,
    tags_original: List[str],
    published_at: str,
    status: str = "pending",
    episode_id: Optional[str] = None,
) -> None:
    conn = get_connection()
    conn.execute(
        """INSERT INTO yt_videos (
                video_id, channel_id, title_original, description_original,
                tags_original, published_at, episode_id, status
               )
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(video_id)
               DO UPDATE SET
                 channel_id=excluded.channel_id,
                 title_original=excluded.title_original,
                 description_original=excluded.description_original,
                 tags_original=excluded.tags_original,
                 published_at=excluded.published_at,
                 episode_id=COALESCE(yt_videos.episode_id, excluded.episode_id),
                 status=excluded.status""",
        (
            video_id,
            channel_id,
            title_original,
            description_original,
            json.dumps(tags_original),
            published_at,
            episode_id,
            status,
        ),
    )
    conn.commit()


def get_videos_by_status(status: str, limit: int = 20) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.execute(
        "SELECT * FROM yt_videos WHERE status = ? ORDER BY published_at DESC LIMIT ?",
        (status, limit),
    )
    rows = [dict(row) for row in cur.fetchall()]
    return rows


def insert_suggestion(
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
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO yt_video_suggestions (
                video_id, language_code, title, description, tags_json,
                hashtags_json, thumbnail_text, pinned_comment,
                playlists_json, created_at
               )
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
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
    return cur.lastrowid


def mark_video_status(video_id: str, status: str) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE yt_videos SET status = ? WHERE video_id = ?",
        (status, video_id),
    )
    conn.commit()
```

---

## 9. `ytseo/youtube_api.py` (Scaffold)

```python
from __future__ import annotations

from typing import Any, Dict, List

# NOTE: This is a scaffold; you will need to fill in real YouTube API auth and calls.


def list_channel_videos(channel_handle: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Return a list of videos for the channel.

    For now, this is a placeholder implementation. Replace with real YouTube Data API logic.
    """
    # TODO: Implement real YouTube API call
    # Placeholder structure:
    return [
        {
            "video_id": f"demo_{i}",
            "channel_id": "demo_channel",
            "title": f"Demo Video {i}",
            "description": "This is a placeholder description.",
            "tags": ["demo", "placeholder"],
            "published_at": "2025-01-01T00:00:00Z",
        }
        for i in range(limit)
    ]


def update_video_metadata(
    video_id: str,
    title: str,
    description: str,
    tags: List[str],
) -> None:
    """Update video metadata on YouTube.

    For now this just logs; replace with YouTube Data API v3 `videos.update` call.
    """
    # TODO: Implement real API update
    print(f"[DRY-RUN] Would update video {video_id}:")
    print(f"  Title: {title!r}")
    print(f"  Description: {description[:80]!r}...")
    print(f"  Tags: {tags}")
```

---

## 10. `ytseo/seo_engine.py` (Stubbed)

```python
from __future__ import annotations

from typing import Any, Dict, List


def generate_title(context: Dict[str, Any]) -> str:
    original = context.get("title_original", "Untitled")
    return f"{original} | Updated SEO"


def generate_description(context: Dict[str, Any]) -> str:
    desc = context.get("description_original", "")
    summary = context.get("summary", "")
    return (
        f"{summary}\n\n"
        f"---\n"
        f"Original description:\n{desc}\n\n"
        f"Subscribe for more Canadian news and analysis."
    )


def generate_tags(context: Dict[str, Any]) -> List[str]:
    base_tags = context.get("tags_original", [])
    extra = ["canada", "canadian news", "the news forum"]
    return list(dict.fromkeys(base_tags + extra))


def generate_hashtags(context: Dict[str, Any]) -> List[str]:
    return ["#Canada", "#CanadianNews", "#TheNewsForum"]


def generate_thumbnail_text(context: Dict[str, Any]) -> List[str]:
    title = context.get("title_original", "Breaking News")
    return [
        title,
        "Key Takeaways Inside",
        "Why This Matters for Canada",
    ]


def generate_pinned_comment(context: Dict[str, Any]) -> str:
    return (
        "Thanks for watching! 🇨🇦\n"
        "Tell us what you think in the comments and subscribe "
        "for more independent Canadian perspectives."
    )


def generate_multilanguage_variants(
    context: Dict[str, Any],
    languages: List[str],
) -> Dict[str, Dict[str, Any]]:
    base_title = generate_title(context)
    base_description = generate_description(context)
    results: Dict[str, Dict[str, Any]] = {}
    for lang in languages:
        # TODO: Replace with real translation.
        results[lang] = {
            "title": f"[{lang}] {base_title}",
            "description": f"[{lang} translation placeholder]\n\n{base_description}",
        }
    return results
```

---

## 11. `cli/main.py` (Typer CLI)

```python
import subprocess
from typing import Optional

import typer

from ytseo.config import load_settings
from ytseo import models, youtube_api, seo_engine


app = typer.Typer(help="YouTube SEO Refresh Tool CLI")


@app.command()
def sync(channel: Optional[str] = None, limit: int = 20) -> None:
    """Sync latest videos from a YouTube channel into the local DB."""
    settings = load_settings()
    channel_handle = channel or settings.default_channel_handle
    videos = youtube_api.list_channel_videos(channel_handle, limit=limit)
    for v in videos:
        models.upsert_channel(v["channel_id"], "Unknown Title")
        models.upsert_video(
            video_id=v["video_id"],
            channel_id=v["channel_id"],
            title_original=v["title"],
            description_original=v.get("description", ""),
            tags_original=v.get("tags", []),
            published_at=v.get("published_at", ""),
        )
    typer.echo(f"Synced {len(videos)} videos from {channel_handle}")


@app.command()
def generate(limit: int = 10) -> None:
    """Generate SEO suggestions for pending videos."""
    pending = models.get_videos_by_status("pending", limit=limit)
    if not pending:
        typer.echo("No pending videos to generate suggestions for.")
        raise typer.Exit(code=0)

    for video in pending:
        context = {
            "title_original": video["title_original"],
            "description_original": video["description_original"],
            "tags_original": [],
        }
        title = seo_engine.generate_title(context)
        description = seo_engine.generate_description(context)
        tags = seo_engine.generate_tags(context)
        hashtags = seo_engine.generate_hashtags(context)
        thumb_texts = seo_engine.generate_thumbnail_text(context)
        pinned = seo_engine.generate_pinned_comment(context)
        # For now, single language 'en' and simple playlists suggestion.
        models.insert_suggestion(
            video_id=video["video_id"],
            language_code="en",
            title=title,
            description=description,
            tags=tags,
            hashtags=hashtags,
            thumbnail_text=thumb_texts[0],
            pinned_comment=pinned,
            playlists=["General"],
        )
        models.mark_video_status(video["video_id"], "suggested")

    typer.echo(f"Generated suggestions for {len(pending)} videos.")


@app.command()
def apply(limit: int = 10) -> None:
    """Apply approved suggestions to YouTube (currently dry-run)."""
    # TODO: Implement querying approved suggestions; for now, just log.
    typer.echo("Apply command is not fully implemented yet (dry-run only).")


@app.command()
def list(status: str = "pending", limit: int = 20) -> None:
    """List videos by status."""
    videos = models.get_videos_by_status(status, limit=limit)
    for v in videos:
        typer.echo(f"{v['video_id']} | {v['published_at']} | {v['title_original']}")


@app.command()
def download(video_id: str) -> None:
    """Download a YouTube video/audio for AI-EWG ingestion (stub)."""
    typer.echo(f"TODO: Implement yt-dlp download for video_id={video_id}")


@app.command()
def ui() -> None:
    """Launch the Streamlit UI."""
    settings = load_settings()
    cmd = [
        "streamlit",
        "run",
        "app/main.py",
        "--server.port",
        str(settings.streamlit_port),
    ]
    typer.echo(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    app()
```

---

## 12. `app/main.py` (Streamlit Entrypoint)

```python
import streamlit as st


st.set_page_config(
    page_title="YouTube SEO Tool",
    layout="wide",
)

st.title("YouTube SEO Refresh Tool")
st.write("Use the pages menu on the left to navigate:")
st.write("- Dashboard")
st.write("- Video List")
st.write("- Video Detail")
st.write("- Settings")
```

---

## 13. `app/pages/01_Dashboard.py`

```python
import streamlit as st

from ytseo import models
from ytseo.db import get_connection


st.title("Dashboard")

conn = get_connection()
total = conn.execute("SELECT COUNT(*) AS c FROM yt_videos").fetchone()["c"]

pending = conn.execute(
    "SELECT COUNT(*) AS c FROM yt_videos WHERE status = 'pending'"
).fetchone()["c"]
suggested = conn.execute(
    "SELECT COUNT(*) AS c FROM yt_videos WHERE status = 'suggested'"
).fetchone()["c"]
approved = conn.execute(
    "SELECT COUNT(*) AS c FROM yt_videos WHERE status = 'approved'"
).fetchone()["c"]
applied = conn.execute(
    "SELECT COUNT(*) AS c FROM yt_videos WHERE status = 'applied'"
).fetchone()["c"]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Videos", total)
col2.metric("Pending", pending)
col3.metric("Suggested", suggested)
col4.metric("Approved", approved)
col5.metric("Applied", applied)

st.info("Daily goal: optimize 5–10 videos per day.")
```

---

## 14. `app/pages/02_Video_List.py`

```python
import streamlit as st

from ytseo.models import get_videos_by_status


st.title("Video List")

status = st.selectbox(
    "Filter by status",
    options=["pending", "suggested", "approved", "applied"],
    index=0,
)
limit = st.slider("Max results", min_value=5, max_value=100, value=20, step=5)

videos = get_videos_by_status(status, limit=limit)

if not videos:
    st.write("No videos found for this status.")
else:
    for v in videos:
        with st.expander(f"{v['video_id']} — {v['title_original']}"):
            st.write(f"Published: {v['published_at']}")
            st.write(f"Status: {v['status']}")
            st.write("Original Description:")
            st.code(v["description_original"][:500] + "...")
            st.write("")
            st.write(f"Episode ID: {v.get('episode_id') or 'N/A'}")
```

---

## 15. `app/pages/03_Video_Detail.py` (Minimal Skeleton)

```python
import streamlit as st
from ytseo.db import get_connection


st.title("Video Detail")

video_id = st.text_input("Video ID")

if video_id:
    conn = get_connection()
    video = conn.execute(
        "SELECT * FROM yt_videos WHERE video_id = ?", (video_id,)
    ).fetchone()
    if not video:
        st.error("Video not found.")
    else:
        st.subheader("Original Metadata")
        st.write(f"Title: {video['title_original']}")
        st.write("Description:")
        st.code(video["description_original"])

        # TODO: Fetch suggestions and display side-by-side.
        st.subheader("SEO Suggestions")
        st.write("Suggestions view is not fully implemented yet.")
else:
    st.info("Enter a Video ID to view details.")
```

---

## 16. `app/pages/04_Settings.py`

```python
import streamlit as st

from ytseo.config import load_settings


st.title("Settings")

settings = load_settings()

st.subheader("Paths")
st.write(f"DB path: `{settings.db_path}`")
st.write(f"YouTube client secret: `{settings.youtube_client_secret_path}`")
st.write(f"AI-EWG DB path: `{settings.ai_ewg_db_path}`")
st.write(f"AI-EWG HTTP URL: `{settings.ai_ewg_http_url}`")

st.subheader("Defaults")
st.write(f"Default channel handle: `{settings.default_channel_handle}`")
st.write(f"Streamlit port: `{settings.streamlit_port}`")

st.info("In the future, this page can be expanded to edit language profiles and integration toggles.")
```

---

## 17. `tests/test_smoke.py`

```python
def test_imports() -> None:
    import ytseo.config  # noqa: F401
    import ytseo.db      # noqa: F401
    import ytseo.models  # noqa: F401
```
