# 🎬 yt-seo-tool

**AI-powered YouTube SEO optimization tool** for Canadian news content. Automatically generates professional titles, descriptions, tags, and more using LLM intelligence enriched with podcast episode data.

## ✨ Features

- 🤖 **LLM-Powered SEO** - Generates optimized metadata using Ollama (llama3.1) or OpenAI
- 🇨🇦 **Canadian News Focus** - Prompts tailored for Canadian news and politics content
- 🎙️ **AI-EWG Integration** - Enriches context with podcast episode data (topics, guests, summaries)
- 🔒 **Multi-Layer Safety** - DRY_RUN mode, manual confirmation, tag merging (never deletes)
- 📊 **Streamlit Dashboard** - Visual workflow for reviewing and approving suggestions
- ⚡ **Priority Processing** - Process videos by recency, age, or AI-EWG linkage
- 🔄 **Status Workflow** - Track videos through pending → suggested → approved → applied states

## Quick start

1) Create and activate a virtual environment (recommended)

2) Install in editable mode:

```
python -m pip install -e .
```

3) **Set up OAuth credentials:**
   - Create a Google Cloud project and enable YouTube Data API v3
   - Download OAuth 2.0 credentials as `config/client_secret.json`
   - See [Google's OAuth setup guide](https://developers.google.com/youtube/v3/guides/authentication)

4) **Configure environment:**

```bash
# Copy and edit environment file
copy .env.example .env

# Edit .env with your settings:
# - AI_EWG_DB_PATH (path to AI-EWG database)
# - OLLAMA_BASE_URL (default: http://localhost:11434)
# - MODEL_NAME (default: llama3.1)
```

5) **Run OAuth flow (first time only):**

```bash
ytseo sync --channel @YourChannel --limit 5
# Opens browser for OAuth authorization
```

## 🚀 Usage

### CLI Commands

**Sync videos from YouTube:**
```bash
ytseo sync --channel @TheNewsForum --limit 20
```

**Generate SEO suggestions:**
```bash
# Process newest videos first (default)
ytseo generate --limit 10 --priority recent

# Process AI-EWG linked videos (best context)
ytseo generate --limit 10 --priority linked

# Process oldest videos (backfill catalog)
ytseo generate --limit 10 --priority oldest
```

**List videos by status:**
```bash
ytseo list --status pending
ytseo list --status suggested
```

**Launch Streamlit UI:**
```bash
ytseo ui --port 8502
```

**Apply approved changes (with safety controls):**
```bash
ytseo apply --limit 5
# Requires manual confirmation by typing "APPLY"
```

### Streamlit UI Pages

**Dashboard** - Overview metrics and daily targets
- Video counts by status (pending, suggested, approved, applied)
- Daily optimization progress
- Recent activity feed

**Video List** - Browse and filter videos
- Filter by status
- View suggestion counts
- Quick actions

**Video Detail** - Side-by-side comparison
- Original vs suggested metadata
- Approve/Regenerate/Reject actions
- Language selector (multi-language ready)
- Suggestion history

**Settings** - Configuration viewer

## 📁 Project Structure

```
yt-seo-tool/
├── cli/                    # Typer CLI entrypoint
├── app/                    # Streamlit UI
│   └── pages/             # Dashboard, Video List, Video Detail
├── ytseo/                 # Core library
│   ├── config.py          # Settings management
│   ├── db.py              # SQLite connection
│   ├── models.py          # Database CRUD
│   ├── youtube_api.py     # YouTube Data API integration
│   ├── seo_engine.py      # LLM-powered SEO generation
│   ├── ai_ewg_bridge.py   # AI-EWG database bridge
│   ├── llm_client.py      # LLM client wrapper
│   └── workflows.py       # High-level workflows
├── migrations/            # Database schema
├── config/                # Configuration files
├── docs/                  # Documentation
│   ├── task.md           # Development checklist
│   ├── SECURITY.md       # Security guidelines
│   └── video_processing_strategy.md
└── tests/                 # Test suite
```

## ⚙️ Configuration

### Environment Variables (`.env`)
```bash
# Database
DB_PATH=data/ytseo.sqlite

# YouTube OAuth
YOUTUBE_CLIENT_SECRET_PATH=config/client_secret.json
DEFAULT_CHANNEL_HANDLE=@TheNewsForum

# AI-EWG Integration
AI_EWG_DB_PATH=../ai-ewg/data/pipeline.db
AI_EWG_HTTP_URL=http://localhost:8000

# LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3.1

# Safety Controls (CRITICAL)
DRY_RUN=true
REQUIRE_CONFIRMATION=true
MERGE_TAGS=true
```

### Safety Controls

**DRY_RUN** (default: `true`)
- Logs changes without applying to YouTube
- Always test with DRY_RUN=true first

**REQUIRE_CONFIRMATION** (default: `true`)
- Requires typing "APPLY" to confirm updates
- Prevents accidental changes

**MERGE_TAGS** (default: `true`)
- Adds new tags, never deletes existing
- Safe tag enrichment

## 🔒 Security

**Never commit these files:**
- `config/client_secret.json` - OAuth credentials
- `token.pickle` - OAuth tokens
- `.env` - Environment variables
- `*.db`, `*.sqlite` - Databases

See `docs/SECURITY.md` for comprehensive security guidelines.

## 🧪 Testing

```bash
# Install test dependencies
python -m pip install pytest

# Run tests
pytest -q
```

## 📚 Documentation

- `docs/task.md` - Development phases and checklist
- `docs/SECURITY.md` - Security best practices
- `docs/video_processing_strategy.md` - Handling large video libraries
- `docs/windsurf_prompt.md` - Original project specification

## 🤝 Contributing

This tool is designed for The News Forum's YouTube channel optimization workflow. Contributions welcome!

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for CLI
- UI powered by [Streamlit](https://streamlit.io/)
- LLM integration via [Ollama](https://ollama.ai/)
- Integrates with [AI-EWG](https://github.com/ramcana/ai-ewg) podcast pipeline
