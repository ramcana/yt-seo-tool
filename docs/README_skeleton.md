# yt-seo-tool

YouTube SEO Refresh Tool for optimizing existing videos on channels like **@TheNewsForum**.

This tool helps you:

- Fetch and sync existing YouTube videos into a local SQLite DB.
- Generate SEO-optimized titles, descriptions, tags, hashtags, and pinned comments.
- Prepare text suggestions for thumbnails.
- Manage a human-in-the-loop approval workflow via a Streamlit UI.
- Eventually apply changes back to YouTube via the YouTube Data API.
- Optionally read enhanced episode metadata from your **AI-EWG** project.

---

## Features (Phase 1)

- Streamlit app with:
  - Dashboard
  - Video list
  - Minimal video detail view
  - Settings
- Typer CLI (`ytseo`) with commands:
  - `sync` – fetch videos from a channel into the DB.
  - `generate` – create SEO suggestions for pending videos.
  - `list` – list videos by status.
  - `apply` – placeholder for applying approved suggestions.
  - `download` – placeholder for downloading video/audio for AI-EWG ingestion.
  - `ui` – launch Streamlit UI.
- SQLite-based persistence with `yt_*` tables.
- Basic SEO engine with clear extension points for LLM integration.

---

## Installation

1. Clone the repo:

   ```bash
   git clone https://github.com/your-org/yt-seo-tool.git
   cd yt-seo-tool
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # on Windows: .venv\Scripts\activate
   pip install -e .
   ```

3. Copy config templates:

   ```bash
   cp config/settings.example.toml config/settings.toml
   cp .env.example .env
   ```

   Edit `config/settings.toml` and `.env` as needed.

---

## YouTube API Setup (High-Level)

1. In Google Cloud Console, create a project and enable:
   - **YouTube Data API v3**
2. Create OAuth 2.0 credentials (Desktop app).
3. Download the client secret JSON as `config/client_secret.json`.
4. The first time you run real YouTube API calls, you’ll go through a browser auth flow and a `token.json` file will be created (to be implemented).

For now, the `youtube_api.py` module is scaffolded and uses placeholder data – you can safely run the app without real YouTube access while wiring up the rest of the system.

---

## Usage

### 1. Initialize the Database

The database is automatically initialized on first use from `migrations/0001_init.sql` when `ytseo.db` does not exist.

### 2. Run the CLI

```bash
ytseo --help
```

Example:

```bash
# Sync placeholder videos (until real API is implemented)
ytseo sync --channel @TheNewsForum --limit 10

# Generate SEO suggestions for pending videos
ytseo generate --limit 5

# List pending videos
ytseo list --status pending --limit 10
```

### 3. Launch the Streamlit UI

```bash
ytseo ui
```

Then open your browser at:

```text
http://localhost:8502
```

---

## AI-EWG Integration (Future)

- `ytseo/ai_ewg_bridge.py` is reserved for reading enhanced episode metadata from AI-EWG:
  - Episode summaries
  - Topics & entities
  - JSON-LD
  - Host/guest info
- The SEO engine can be extended to include this richer context when generating metadata.

---

## Roadmap

- [ ] Implement real YouTube Data API calls in `youtube_api.py`.
- [ ] Implement apply flow (`ytseo apply`) to update video metadata.
- [ ] Add support for multi-language metadata and translations.
- [ ] Integrate YouTube Analytics API for performance-based SEO iteration.
- [ ] Tighten AI-EWG bridge and link videos ↔ episodes.

---

## License

Internal project – choose and add a license if needed.
