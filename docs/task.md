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
* [ ] **Define mapping strategy video ↔ episode**

  * [ ] Add `episode_id` manually for a test set (e.g., via DB or a temp UI).
  * [ ] Later: add a smarter mapping (by title/date).
* [ ] **Enrich `context` in `workflows.generate`**

  * [ ] For each `video`, if an `episode_id` exists:
    - Fetch AI-EWG episode summary, topics, entities.
    - Inject into `context`:
    - `summary`
    - `topics`
    - `entities`
    - `hosts`
    - `guests`
* [ ] **Update prompt templates to use AI-EWG fields**

  * [ ] Mention show/host/guest explicitly when present.
  * [ ] Use topics & entities to bias SEO keywords.
* [ ] **Test enriched generation**

  * [ ] Attach 3–5 videos to known AI-EWG episodes.
  * [ ] Run `ytseo generate --limit 5`.
  * [ ] Confirm descriptions feel *smarter* than pure YouTube-only context.

---

## Phase 10: Streamlit UX Upgrade (Real Data & Workflow)

* [ ] **Video List improvements**

  * [ ] Show count of suggestions per video.
  * [ ] Add badge/colour for status (pending/suggested/approved/applied).
  * [ ] Add quick action: “Open in Detail view”.
* [ ] **Video Detail view full implementation**

  * [ ] Fetch original metadata + the latest suggestion for selected `video_id`.
  * [ ] Show **side-by-side layout**:

    * Left: original title/desc/tags.
    * Right: suggested title/desc/tags/hashtags/thumb text/pinned comment.
  * [ ] Add **language dropdown** (even if only “en” at first).
  * [ ] Add **Approve** button:

    * [ ] Set video `status = 'approved'`.
  * [ ] Add **Regenerate** button:

    * [ ] Calls `seo_engine` again and writes a new suggestion row.
* [ ] **Diff / visual clarity**

  * [ ] Highlight changed fields (e.g., use markdown or simple diff).
* [ ] **Daily workflow visibility**

  * [ ] On Dashboard, show:

    * [ ] “Videos optimized today” (approved+applied).
    * [ ] “Remaining to hit daily target” (5–10).

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

## ✅ Intelligence & Integration Phase Complete (Target State)

Once you’ve worked through Phases 7–12, you’ll have:

### What’s working then:

* ✅ Real YouTube Data API sync & (optionally) metadata updates
* ✅ LLM-powered SEO engine with prompts tuned to your editorial style
* ✅ Optional AI-EWG enrichment for deeper understanding of episodes
* ✅ Streamlit UI that supports:

  * Reviewing suggestions
  * Approving per video
  * Seeing daily progress
* ✅ Multi-language metadata model in place (even if only EN is used initially)
* ✅ Safe, DRY-RUN-capable `apply` flow with DB audit trail

### Natural next iterations after that:

1. Fine-tune prompt templates for show/host/guest styles.
2. Add AI-EWG-based **clip / chapter suggestions** to descriptions.
3. Integrate analytics into SEO decisions (e.g., “revise low-CTR titles”).
4. Add bulk approval / bulk apply flows for high-confidence rules.
5. Expose a “review queue” for a human editor to work through daily.


