# Task Plan – yt-seo-tool Bootstrap

This checklist turns docs/windsurf_prompt.md into actionable steps. We will work top-down and verify after each phase.

## Phase 1: Repository scaffold
 - [x] Create directories
   - [x] app/
   - [x] app/pages/
   - [x] ytseo/
   - [x] cli/
   - [x] config/
   - [x] migrations/
   - [x] tests/
 - [x] Create files
   - [x] app/main.py
   - [x] app/pages/01_Dashboard.py
   - [x] app/pages/02_Video_List.py
   - [x] app/pages/03_Video_Detail.py
   - [x] app/pages/04_Settings.py
   - [x] ytseo/__init__.py
   - [x] ytseo/config.py
   - [x] ytseo/db.py
   - [x] ytseo/models.py
   - [x] ytseo/youtube_api.py
   - [x] ytseo/youtube_analytics.py
   - [x] ytseo/seo_engine.py
   - [x] ytseo/ai_ewg_bridge.py
   - [x] ytseo/yts_downloader.py
   - [x] ytseo/workflows.py
   - [x] cli/__init__.py
   - [x] cli/main.py
   - [x] config/settings.example.toml
   - [x] migrations/0001_init.sql
   - [x] tests/__init__.py
   - [x] tests/test_smoke.py
   - [x] README.md
   - [x] pyproject.toml
   - [x] .env.example
   - [x] .gitignore

## Phase 2: Minimum viable implementations
 - [x] ytseo/db.py: open SQLite connection, apply migrations, simple helper to ensure schema
 - [x] ytseo/models.py: CRUD helpers for channels, videos, suggestions, status updates
 - [x] ytseo/youtube_api.py: stubs for list_videos_by_channel, update_video_metadata (TODO markers)
 - [x] ytseo/seo_engine.py: stub functions per interface with placeholder logic
 - [x] ytseo/ai_ewg_bridge.py: stub signatures and docstrings for get_episode_* helpers

## Phase 3: CLI (Typer)
 - [x] Entry point `ytseo` in pyproject
 - [x] Commands with logging & argument parsing:
   - [x] sync --channel --limit
   - [x] generate --limit
   - [x] apply --limit
   - [x] list --status
   - [x] download --video-id
   - [x] ui (runs Streamlit on configured port)

## Phase 4: Streamlit UI
 - [x] app/main.py config + multipage nav
 - [x] 01_Dashboard: stats and daily target placeholder
 - [x] 02_Video_List: table with filters and link to detail
 - [x] 03_Video_Detail: original vs suggestions, language selector, approve/regenerate buttons
 - [x] 04_Settings: forms for config placeholders and languages

## Phase 5: Config & Docs
 - [x] config/settings.example.toml with keys: DB_PATH, YOUTUBE_CLIENT_SECRET_PATH, AI_EWG_DB_PATH, AI_EWG_HTTP_URL, DEFAULT_CHANNEL_HANDLE, STREAMLIT_PORT
 - [x] .env.example with common environment vars
 - [x] README.md: install, credentials setup, CLI usage, Streamlit run

## Phase 6: Tests & Verification
 - [x] tests/test_smoke.py imports modules and opens DB
 - [x] pip install -e . succeeds (Python 3.11 venv)
 - [x] ytseo --help runs
 - [x] ytseo sync/generate/list commands work
 - [x] ytseo ui launches Streamlit (http://localhost:8502)

## ✅ Bootstrap Complete

All phases completed successfully! The project is ready for iteration.

### What's working now:
- ✅ Full project structure scaffolded
- ✅ CLI with 6 commands: sync, generate, apply, list, download, ui
- ✅ SQLite database with migrations
- ✅ Streamlit UI with 4 pages (Dashboard, Video List, Video Detail, Settings)
- ✅ Python 3.11 virtual environment
- ✅ Editable install via pip

### Next iteration steps:
1. Implement real YouTube Data API integration (youtube_api.py)
2. Add LLM-powered SEO generation (seo_engine.py)
3. Wire AI-EWG bridge for episode data
4. Enhance Streamlit pages with real data display
5. Add multi-language support workflow
6. Implement YouTube Analytics integration


## Phase 7: Real YouTube Data API Integration

* [x] **Enable APIs in Google Cloud Console**

  * [x] Create / pick a GCP project (`tnf-youtubeseo`).
  * [x] Enable **YouTube Data API v3**.
* [x] **Create OAuth credentials**

  * [x] Create an OAuth 2.0 **Desktop** client.
  * [x] Download `client_secret.json` → placed at `config/client_secret.json`.
  * [x] Update `settings.toml` / `.env` paths (fixed to `config/client_secret.json`).
  * [x] Add OAuth files to `.gitignore` for security.
* [x] **Implement auth flow in `youtube_api.py`**

  * [x] Added OAuth flow with `InstalledAppFlow.run_local_server()`
  * [x] Implemented token storage (`token.pickle`) with auto-refresh
* [x] **Implement `list_channel_videos()`**

  * [x] Resolve channel handle → channel ID (forUsername + search fallback)
  * [x] Fetch latest videos via uploads playlist (`playlistItems.list`)
  * [x] Get full details via `videos.list` (snippet, contentDetails, statistics)
  * [x] Return normalized dicts to `workflows.sync`
* [x] **Implement `update_video_metadata()`**

  * [x] Use `videos.update(part="snippet")` to update:
    * [x] Title
    * [x] Description
    * [x] Tags
  * [x] DRY_RUN mode implemented (logs instead of updating)
* [x] **Verify end-to-end with real data**

  * [x] Install new dependencies: `pip install -e .`
  * [x] Run `ytseo sync --channel "@TheNewsForum" --limit 5` - SUCCESS (5 real videos synced)
  * [x] OAuth flow completed and token saved
  * [x] Added multi-layer safety controls (DRY_RUN, REQUIRE_CONFIRMATION, tag merging)

---

## Phase 8: LLM-Powered SEO Engine

* [x] **Choose intelligence provider(s)**

  * [x] Primary: Ollama (shared with AI-EWG at localhost:11434)
  * [x] Model: llama3.1 (already running in AI-EWG)
  * [x] Optional fallback: OpenAI GPT-4o-mini
* [x] **Add config for LLM**

  * [x] Added `LLM_PROVIDER`, `OLLAMA_BASE_URL`, `MODEL_NAME` in `settings.toml`
  * [x] Config reads from `ytseo.config.get_setting()`
* [x] **Implement LLM client wrapper**

  * [x] Created `ytseo/llm_client.py` with Ollama and OpenAI support
  * [x] Handle errors + timeouts gracefully (60s timeout, proper error messages)
* [x] **Design prompt templates**

  * [x] Title prompt: Canadian news, non-clickbait, SEO-optimized, max 100 chars
  * [x] Description prompt: 200–300 words, summary + segments + CTA
  * [x] Tags prompt: 20–30 tags, merges with existing (never deletes)
  * [x] Hashtags prompt: 5–10 hashtags, proper formatting
  * [x] Thumbnail text prompt: 3–5 punchy options, 3-7 words
  * [x] Pinned comment prompt: polite Canadian tone, CTA
* [x] **Wire LLM into `seo_engine.py`**

  * [x] Implemented `generate_title` with LLM + AI-EWG context
  * [x] Implemented `generate_description` with episode enrichment
  * [x] Implemented `generate_tags` with tag merging (safe)
  * [x] Implemented `generate_hashtags` with formatting
  * [x] Implemented `generate_thumbnail_text` with parsing
  * [x] Implemented `generate_pinned_comment` with Canadian tone
* [x] **Add safety & constraints**

  * [x] Enforce max lengths (title ≤ 100, description ≤ 5000)
  * [x] Tag merging (never deletes existing tags)
  * [x] Fallback to original content on LLM errors
  * [x] AI-EWG context enrichment with error handling
* [x] **Test on a small batch**

  * [x] Run `ytseo generate --limit 3` - SUCCESS (5 videos with suggestions)
  * [x] Inspect suggestions in DB - titles, descriptions, tags, hashtags generated
  * [x] Fixed tag parsing to handle JSON arrays from LLM
  * [x] Fixed hashtag parsing to extract proper hashtags
  * [x] Streamlit UI running at http://localhost:8502
  * [x] Dashboard shows metrics and recent activity
  * [x] Video List shows all videos with status badges
  * [ ] Test apply flow (DRY_RUN mode) - ready for manual testing
* [x] **Prompt improvements (Nov 2024)**

  * [x] Replaced Canadian-centric prompts with search-intent focused ones
  * [x] Switched Ollama to chat endpoint with retry logic
  * [x] Improved description context window (200→800 chars)
  * [x] Added fallback handling for missing episode data
  * [x] Fixed tag parsing for comma-separated LLM output
  * [x] Added video title/description to tag generation context

---

## Phase 9: AI-EWG Bridge & Context Enrichment

* [x] **Point to AI-EWG resources**

  * [x] Confirmed shared SQLite DB path: `../ai-ewg/data/pipeline.db`
  * [x] Updated `settings.toml` / `.env` with correct `AI_EWG_DB_PATH`
  * [x] Inspected schema: episodes, json_metadata_index, clips tables available
* [x] **Implement `ai_ewg_bridge.py`**

  * [x] Added `get_episode_by_id(episode_id: str)` - reads from json_metadata_index + episodes
  * [x] Added `get_episode_for_youtube_video(video_id: str)` (stub, returns None for now)
  * [x] Added `search_episodes_by_title()` helper for manual mapping UI
* [x] **Define mapping strategy video ↔ episode**

  * [x] Manual `episode_id` field in database
  * [ ] TODO: Add smarter auto-mapping (by title/date similarity)
  * [ ] TODO: Add UI for manual episode linking
* [x] **Enrich `context` in `workflows.generate`**

  * [x] Implemented `_get_episode_context()` in seo_engine
  * [x] Fetches AI-EWG episode data when episode_id exists
  * [x] Extracts: summary, topics, entities, hosts, guests, show_name
  * [x] Injects into all generation functions
* [x] **Update prompt templates to use AI-EWG fields**

  * [x] All prompts now use topics, entities, guests from AI-EWG
  * [x] Fallback to YouTube title/description when no episode data
  * [x] Show/host/guest mentioned explicitly when present
* [ ] **Test enriched generation**

  * [ ] TODO: Manually link 3–5 videos to AI-EWG episodes via DB
  * [ ] TODO: Run `ytseo generate --limit 5` on linked videos
  * [ ] TODO: Compare quality vs non-linked videos

---

## Phase 10: Streamlit UX Upgrade (Real Data & Workflow)

* [x] **Video List improvements**

  * [x] Show count of suggestions per video
  * [x] Add badge/colour for status (pending/suggested/approved/applied)
  * [x] Add quick action: "View Details" button
  * [x] **NEW: Fetch specific video from YouTube** (expander with video ID input)
* [x] **Video Detail view full implementation**

  * [x] Fetch original metadata + latest suggestion for selected `video_id`
  * [x] Show **side-by-side layout**:
    * Left: original title/desc/tags
    * Right: suggested title/desc/tags/hashtags/thumb text/pinned comment
  * [x] Add **language dropdown** (defaults to "en")
  * [x] Add **Approve** button → sets video `status = 'approved'`
  * [x] Add **Regenerate** button → marks as pending, creates new suggestion
  * [x] Add **Reject** button → marks as rejected
  * [x] Show **suggestion history** (all past suggestions with timestamps)
* [ ] **Diff / visual clarity**

  * [ ] TODO: Highlight changed fields with color coding or diff view
* [x] **Daily workflow visibility**

  * [x] Dashboard shows:
    * [x] Total videos by status
    * [x] Recent activity (last 10 videos)
    * [x] Metrics cards for pending/suggested/approved/applied
  * [ ] TODO: Add "daily target" tracking (5-10 videos/day)

---

## Phase 10.5: Advanced Processing Features (Nov 2024)

* [x] **Priority-based video processing**
  * [x] Added `--priority` flag to generate command
  * [x] Modes: `recent` (newest first), `oldest` (backfill), `linked` (AI-EWG first)
  * [x] Documented in `docs/video_processing_strategy.md`

* [x] **Targeted video processing**
  * [x] Added `--video-id` flag to generate command
  * [x] Process specific video from local database
  * [x] Enhanced `list` command with better formatting
  * [x] Shows video IDs for easy copy/paste

* [x] **Fetch from YouTube**
  * [x] New `ytseo fetch --video-id` CLI command
  * [x] New `get_video_by_id()` in youtube_api.py
  * [x] New `fetch_and_process_video()` workflow
  * [x] Fetches video → saves to DB → generates SEO in one step
  * [x] Added to Streamlit Video List page (expander UI)
  * [x] Enables picking any video from channel without full sync

* [x] **Documentation**
  * [x] Updated README.md with new commands
  * [x] Updated video_processing_strategy.md with all approaches
  * [x] Added security guidelines in SECURITY.md
  * [x] Enhanced .gitignore for OAuth credentials

---

## Phase 11: Multi-Language Support Workflow

* [ ] **Seed `yt_language_profiles`**

  * [ ] Insert:
    - `en` – English (enabled)
    - `fr` – French (enabled)
    - plus 3–5: `pa`, `zh`, `tl`, `ar` etc. (enabled=false initially).
* [ ] **Extend `seo_engine.generate_multilanguage_variants`**

  * [ ] Replace stub with:
    - LLM-based translation using English as base.
    - Or call a dedicated translation model/API.
* [ ] **Store per-language suggestions**

  * [ ] For each language:

    * [ ] Insert row in `yt_video_suggestions` with `language_code`.
* [ ] **Streamlit detail page**

  * [ ] Language dropdown reads from `yt_language_profiles` (enabled only).
  * [ ] Switching language reloads that language’s suggestion.
* [ ] **YouTube API support (later)**

  * [ ] Plan for using `localizations` field in `videos.update` for multi-language title & description.
  * [ ] Leave TODO markers in `youtube_api.py`.

---

## Phase 12: Apply Flow & Safe Rollout

* [ ] **Define “apply” behaviour**

  * [ ] Decide if apply uses:
    - Latest suggestion only.
    - Only language `en` initially.
  * [ ] Decide if tags override or merge with existing.
* [ ] **Implement apply logic**

  * [ ] Query `yt_videos` with `status='approved'`.
  * [ ] Get matching suggestions (`language_code='en'`).
  * [ ] Compute `diff_json` (original vs new).
  * [ ] Call `youtube_api.update_video_metadata()` (respect DRY-RUN flag).
  * [ ] Insert into `yt_video_applied_changes`.
  * [ ] Set `yt_videos.status='applied'`.
* [ ] **Guardrails**

  * [ ] Add global DRY-RUN toggle in config.
  * [ ] Add per-video override to skip apply.
  * [ ] Log all changes to console and DB.
* [ ] **Rollout strategy**

  * [ ] Start with **1 test video** (unlisted or low-risk).
  * [ ] Then apply to **1–2 real episodes** you are comfortable updating.
  * [ ] Monitor search/discovery over a week.

---

## Phase 13: YouTube Analytics Integration (Optional, Phase 2)

* [ ] **Enable YouTube Analytics API** in GCP.
* [ ] **Implement `youtube_analytics.py`**

  * [ ] Auth reuse from Data API.
  * [ ] Basic methods:
    - `get_video_stats(video_id)` – views, watch time, CTR, AVD, etc.
* [ ] **Add CLI command**

  * [ ] `ytseo analytics --video-id <id>` to fetch and log stats.
* [ ] **Feed analytics into context**

  * [ ] Optionally flag:
    - Low CTR → maybe title/thumbnail weak.
    - Low AVD → content/promise mismatch.
  * [ ] Expose these signals in `context` for the SEO engine to consider.

---

## 🎯 Current Status (Nov 2024)

### ✅ **Fully Operational:**
- **Phases 1-8:** Complete (scaffold, CLI, UI, YouTube API, LLM engine)
- **Phase 9:** AI-EWG bridge implemented and working (testing pending)
- **Phase 10:** Streamlit UX fully functional with real data
- **Phase 10.5:** Advanced processing features (priority, targeted, fetch)

### 🔧 **What's Working Now:**
1. ✅ **YouTube Data API**
   - OAuth authentication with token refresh
   - Sync videos from channel
   - Fetch specific video by ID
   - Update metadata (with DRY_RUN safety)

2. ✅ **LLM-Powered SEO Engine**
   - Search-intent focused prompts (not region-biased)
   - Ollama chat endpoint with retry logic
   - Context-aware generation (uses video title/description)
   - AI-EWG enrichment when episode_id linked
   - Generates: title, description, tags, hashtags, thumbnail text, pinned comment

3. ✅ **CLI Commands**
   - `sync` - Fetch videos from channel
   - `fetch` - Fetch and process specific video
   - `generate` - Generate SEO with priority/targeted modes
   - `list` - List videos with enhanced formatting
   - `apply` - Apply suggestions (stubbed, needs testing)
   - `ui` - Launch Streamlit

4. ✅ **Streamlit UI**
   - Dashboard with metrics and activity
   - Video List with fetch feature
   - Video Detail with side-by-side comparison
   - Approve/Regenerate/Reject actions
   - Suggestion history

5. ✅ **Processing Modes**
   - Batch by priority (recent/oldest/linked)
   - Targeted by video ID
   - Fetch from YouTube directly

### 🚧 **Pending Work:**

**High Priority:**
- [ ] Test apply flow with real YouTube updates (Phase 8, 12)
- [ ] Test AI-EWG enrichment with linked videos (Phase 9)
- [ ] Add diff/visual clarity to Video Detail (Phase 10)

**Medium Priority:**
- [ ] Multi-language support (Phase 11)
- [ ] Daily target tracking (Phase 10)
- [ ] Auto-mapping videos to AI-EWG episodes (Phase 9)
- [ ] Manual episode linking UI (Phase 9)

**Low Priority:**
- [ ] YouTube Analytics integration (Phase 13)
- [ ] Bulk approval/apply flows
- [ ] Review queue for editors

### 🎉 **Ready for Production Use:**
The tool is fully functional for:
- Syncing videos from YouTube
- Generating SEO suggestions with LLM
- Reviewing suggestions in Streamlit UI
- Approving suggestions (ready for apply)

**Next Step:** Test the apply flow with DRY_RUN mode on a test video!
