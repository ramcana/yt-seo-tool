# yt-seo-tool – Repo Scaffold

This document describes the **initial file and folder structure** for the `yt-seo-tool` repository and includes starter code templates for the main components.

---

## 1. Directory Layout

```text
yt-seo-tool/
  app/
    main.py
    pages/
      01_Dashboard.py
      02_Video_List.py
      03_Video_Detail.py
      04_Settings.py
  ytseo/
    __init__.py
    config.py
    db.py
    models.py
    youtube_api.py
    youtube_analytics.py
    seo_engine.py
    ai_ewg_bridge.py
    yts_downloader.py
    workflows.py
  cli/
    __init__.py
    main.py
  config/
    settings.example.toml
  migrations/
    0001_init.sql
  tests/
    __init__.py
    test_smoke.py
  README.md
  pyproject.toml
  .env.example
  .gitignore
```

---

## 2. Core Python Modules (High-Level Overview)

### 2.1 `ytseo/config.py`
- Loads configuration from environment variables and optional `settings.toml`.
- Provides a simple `Settings` object with:
  - `db_path`
  - `youtube_client_secret_path`
  - `ai_ewg_db_path`
  - `ai_ewg_http_url`
  - `default_channel_handle`
  - `streamlit_port`

### 2.2 `ytseo/db.py`
- Manages SQLite connections.
- Runs migrations on startup (executes `migrations/0001_init.sql` if tables are missing).
- Provides a `get_connection()` function and simple context manager helpers.

### 2.3 `ytseo/models.py`
- Thin convenience layer over `db.py`.
- Implements CRUD helpers for:
  - `yt_channels`
  - `yt_videos`
  - `yt_video_suggestions`
  - `yt_language_profiles`
  - `yt_sync_log`

### 2.4 `ytseo/youtube_api.py`
- Wraps YouTube Data API:
  - Auth handling (OAuth-based; use client secrets JSON).
  - `list_channel_videos(channel_handle, limit)`
  - `get_video_details(video_id)`
  - `update_video_metadata(video_id, title, description, tags)`
- For now, functions can be stubbed but structured.

### 2.5 `ytseo/seo_engine.py`
- Responsible for generating SEO metadata:
  - Titles
  - Descriptions
  - Tags
  - Hashtags
  - Thumbnail text
  - Pinned comment
  - Multilanguage variants
- Contains placeholder implementations with clear TODOs for LLM integration.

### 2.6 `ytseo/workflows.py`
- Orchestrates:
  - Sync process (fetch from YouTube → store in DB).
  - Generate SEO suggestions → store suggestions.
  - Apply approved suggestions → call YouTube API → record applied changes.

### 2.7 `cli/main.py`
- Typer CLI exposing commands:
  - `sync`
  - `generate`
  - `apply`
  - `list`
  - `download`
  - `ui`

### 2.8 `app/main.py` + pages
- Streamlit app with 4 pages:
  - Dashboard
  - Video List
  - Video Detail
  - Settings

---

## 3. Migrations: `migrations/0001_init.sql`

The first migration creates all necessary `yt_*` tables. This script is executed by `ytseo/db.py` on first run.

---

## 4. Testing: `tests/test_smoke.py`

A basic smoke test that verifies imports and DB initialization.

---

Use this document as a reference when building or reviewing the repo structure.
