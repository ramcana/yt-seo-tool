# Windsurf Project Bootstrap Prompt – `yt-seo-tool`

You are Windsurf, acting as an AI IDE with full access to my existing `ai-ewg` project and a new repo that we are about to create called **`yt-seo-tool`**.

I want you to **scaffold and implement a new standalone repository** called **`yt-seo-tool`** with the following constraints and goals:

---

## 1. Project Purpose

`yt-seo-tool` is a **YouTube SEO Refresh Tool** that:

- Works on **already-uploaded YouTube videos** (initially for `@TheNewsForum`).
- Helps me update and optimize:
  - Titles
  - Descriptions
  - Tags
  - Hashtags
  - Thumbnail text ideas (text only)
  - Suggested playlists
  - Pinned comments
- Supports **multi-language metadata**:
  - English, French, plus up to 5 other popular Canadian languages (e.g., Punjabi, Mandarin, Tagalog, Arabic – keep the list configurable).
- Works with a **manual review flow first**, but is architected so we can later:
  - Apply changes automatically using the YouTube Data API.
  - Use YouTube Analytics API for performance-based SEO iterations.

The tool should be **separate from AI-EWG**, but capable of:
- Reading from a **shared SQLite DB** used by AI-EWG (read-only for EWG tables).
- Optionally reading AI-EWG’s JSON outputs for episodes (e.g., summaries, topics, JSON-LD).

---

## 2. High-Level Tech Stack

- **Language**: Python 3.10+
- **UI**: Streamlit web app running on a separate port (e.g., 8502)
- **CLI**: Typer-based CLI named `ytseo`
- **DB**: SQLite (possibly the same file as AI-EWG, with separate `yt_*` tables)
- **YouTube API**:
  - YouTube Data API v3
  - (Later) YouTube Analytics API
- **Optional Downloader**: `yt-dlp` or similar for pulling audio/video from YouTube when needed.
- **LLM/SEO Engine**: Keep LLM calls abstracted so I can plug in OpenAI / local LLM / other providers.

---

## 3. Repository Structure to Create

Please create the following layout in the new repo:

```text
yt-seo-tool/
  app/
    main.py                # Streamlit entrypoint
    pages/
      01_Dashboard.py
      02_Video_List.py
      03_Video_Detail.py
      04_Settings.py
  ytseo/
    __init__.py
    config.py              # Load settings (env variables, config file)
    db.py                  # DB connection & initialization
    models.py              # Typed models or simple ORM-style helpers
    youtube_api.py         # YouTube Data API integration
    youtube_analytics.py   # (Scaffold only, can be TODO)
    seo_engine.py          # SEO generation logic (LLM abstraction)
    ai_ewg_bridge.py       # Read-only access to AI-EWG data
    yts_downloader.py      # Optional YouTube download logic
    workflows.py           # High-level sync/generate/apply workflows
  cli/
    __init__.py
    main.py                # Typer CLI entrypoint (`ytseo`)
  config/
    settings.example.toml
  migrations/
    0001_init.sql          # Initial schema for yt_* tables
  tests/
    __init__.py
    test_smoke.py
  README.md
  pyproject.toml
  .env.example
  .gitignore
```

You don’t have to fully implement everything on the first pass, but you **must** scaffold all the files above and implement functional, minimal versions for:

- `ytseo/db.py`
- `ytseo/models.py`
- `ytseo/youtube_api.py` (with stubbed API calls and clear TODOs)
- `ytseo/seo_engine.py` (with stub functions and comments where to plug LLM)
- `app/main.py` and Streamlit pages
- `cli/main.py` with Typer commands for:
  - `sync`
  - `generate`
  - `apply`
  - `list`
  - `download`
  - `ui`

---

## 4. Database Design Requirements

We are using **SQLite**. You should assume either:
- A dedicated DB file for `yt-seo-tool`; OR
- A shared DB file with AI-EWG (in which case `yt_*` tables must not conflict).

Please create the following tables (via SQL in `migrations/0001_init.sql` and helper methods in `db.py` / `models.py`):

- `yt_channels`
  - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
  - `channel_id` (TEXT UNIQUE)
  - `title` (TEXT)
  - `last_synced` (TEXT ISO-8601)

- `yt_videos`
  - `video_id` (TEXT PRIMARY KEY)
  - `channel_id` (TEXT)
  - `title_original` (TEXT)
  - `description_original` (TEXT)
  - `tags_original` (TEXT as JSON)
  - `published_at` (TEXT ISO-8601)
  - `episode_id` (TEXT, nullable)
  - `status` (TEXT: 'pending' | 'suggested' | 'approved' | 'applied')

- `yt_video_suggestions`
  - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
  - `video_id` (TEXT)
  - `language_code` (TEXT)
  - `title` (TEXT)
  - `description` (TEXT)
  - `tags_json` (TEXT)
  - `hashtags_json` (TEXT)
  - `thumbnail_text` (TEXT)
  - `pinned_comment` (TEXT)
  - `playlists_json` (TEXT)
  - `created_at` (TEXT)

- `yt_video_applied_changes`
  - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
  - `video_id` (TEXT)
  - `diff_json` (TEXT)
  - `applied_at` (TEXT)

- `yt_language_profiles`
  - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
  - `code` (TEXT)
  - `label` (TEXT)
  - `enabled` (INTEGER as boolean)

- `yt_sync_log`
  - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
  - `run_date` (TEXT)
  - `count_fetched` (INTEGER)
  - `notes` (TEXT)

Implement simple helpers in `models.py` for:
- Creating/updating channels
- Creating/updating videos
- Creating/read suggestions
- Marking suggestions as approved/applied

---

## 5. CLI Requirements

Implement a Typer-based CLI in `cli/main.py` exposed via an entry point (in `pyproject.toml`) as `ytseo`.

Commands (with placeholder logic OK, but structure must be correct):

1. `ytseo sync --channel @TheNewsForum --limit 20`
   - Uses `ytseo.youtube_api` to fetch latest videos from a given channel.
   - Stores/updates video rows in `yt_videos` and `yt_channels`.

2. `ytseo generate --limit 10`
   - Finds videos with `status='pending'` and no suggestions yet.
   - Calls `ytseo.seo_engine` to generate suggestions.
   - Stores in `yt_video_suggestions` and updates video `status` to `suggested`.

3. `ytseo apply --limit 10`
   - Finds videos with `status='approved'` and applies metadata to YouTube using `youtube_api.update_video_metadata`.
   - Writes a record into `yt_video_applied_changes` and sets `status='applied'`.
   - For now, you can stub the API call with a log + TODO.

4. `ytseo list --status pending`
   - Lists videos filtered by status.

5. `ytseo download --video-id <id>`
   - Uses `yts_downloader.py` to download audio/video to a configured folder.
   - That folder can later be ingested by AI-EWG (no direct coupling required in this step).

6. `ytseo ui`
   - Runs the Streamlit app (`streamlit run app/main.py --server.port 8502`).

Each command should be implemented with logging, proper argument parsing, and clearly marked TODOs where real YouTube/LLM integration will happen.

---

## 6. Streamlit UI Requirements

Create a 4-page Streamlit app with the following behavior:

### 6.1 `app/main.py`
- Configures page, sets up navigation for the multipage app.
- Acts as the root launcher for the pages under `app/pages`.

### 6.2 Pages

**01_Dashboard.py**
- Shows high-level stats from the DB:
  - Total videos
  - Videos by status
  - Daily SEO target (5–10) and current day’s progress (placeholder calculation)

**02_Video_List.py**
- Table/grid listing videos from `yt_videos`.
- Filters by:
  - Status
  - Date range (optional)
- Actions:
  - Button to open detail view (link to Video Detail page using query params or session state).

**03_Video_Detail.py**
- Side-by-side display:
  - Original metadata (left)
  - Suggested metadata (right; based on `yt_video_suggestions`)
- Ability to select language (dropdown from `yt_language_profiles`).
- Buttons:
  - "Mark as Approved" (sets video status to `approved`)
  - "Regenerate Suggestions" (calls `seo_engine` again)

**04_Settings.py**
- Form to view/edit:
  - DB path (read-only display or environment value)
  - YouTube API credentials (just text fields/placeholders, actual secrets stay in `.env`)
  - Languages enabled (`yt_language_profiles` records)
  - AI-EWG integration settings (`AI_EWG_DB_PATH`, `AI_EWG_HTTP_URL` as environment variables)

---

## 7. SEO Engine Requirements (`seo_engine.py`)

Implement a module that exposes functions like:

- `generate_title(context: dict) -> str`
- `generate_description(context: dict) -> str`
- `generate_tags(context: dict) -> list[str]`
- `generate_hashtags(context: dict) -> list[str]`
- `generate_thumbnail_text(context: dict) -> list[str]`
- `generate_pinned_comment(context: dict) -> str`
- `generate_multilanguage_variants(context: dict, languages: list[str]) -> dict[lang, dict]`

For now, the implementation can be simple, rule-based, or even stubbed with obvious placeholder text, but the **interfaces must be in place** and clearly documented so I can later plug in an LLM.

`context` should be able to accept:
- Original YouTube metadata
- Optional AI-EWG data (summary, topics, entities)
- Manual notes (later)

---

## 8. AI-EWG Bridge (`ai_ewg_bridge.py`)

Create a small bridge module to:
- Optionally connect to the shared SQLite DB used by AI-EWG.
- Provide helper functions like:
  - `get_episode_by_id(episode_id: str) -> dict`
  - `get_episode_by_youtube_id(video_id: str) -> dict | None` (future)
- These helpers can be stubbed or left as TODO with function signatures and docstrings.

We will later use this to incorporate:
- Summaries
- JSON-LD
- Topics
- Entities
- Host/guest information

---

## 9. Config & README

- `config/settings.example.toml` should include:
  - `DB_PATH`
  - `YOUTUBE_CLIENT_SECRET_PATH`
  - `AI_EWG_DB_PATH`
  - `AI_EWG_HTTP_URL`
  - `DEFAULT_CHANNEL_HANDLE`
  - `STREAMLIT_PORT`
- `.env.example` should include environment variables commonly used.
- `README.md` should explain:
  - What the project is
  - How to install dependencies (`pip install -e .`)
  - How to set up YouTube API credentials
  - How to run CLI commands
  - How to run the Streamlit app

---

## 10. Style & Quality

- Use clear, typed function signatures where reasonable.
- Add docstrings for public functions and modules.
- Avoid over-engineering; keep it straightforward, but **modular and extensible**.
- Add at least one simple test in `tests/test_smoke.py` that imports main modules and connects to the DB.

---

## 11. What to Do Now

1. Create all the files and directories listed above.
2. Populate them with initial implementations and TODO markers.
3. Ensure the project can:
   - Install via `pip install -e .` (or similar)
   - Initialize the DB (apply `0001_init.sql`)
   - Run the CLI `ytseo --help`
   - Launch the Streamlit app with `ytseo ui`

When you’re done scaffolding and wiring the essentials, we’ll iterate on:
- Actual YouTube Data API calls
- Actual SEO text generation (LLM-powered)
- AI-EWG integration.
