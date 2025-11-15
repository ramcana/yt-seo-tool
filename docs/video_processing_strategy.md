# Video Processing Strategy

## Overview
When dealing with large video libraries (100s or 1000s of videos), efficient processing is critical to manage LLM costs, time, and prioritize high-value content.

## Current Implementation

### 1. Controlled Sync
```bash
ytseo sync --channel @TheNewsForum --limit 50
```
- Fetches latest N videos from YouTube
- Prevents overwhelming the database
- Default: 20 videos per sync

### 2. Priority-Based Generation
```bash
# Process newest videos first (default)
ytseo generate --limit 10 --priority recent

# Process oldest videos (backfill catalog)
ytseo generate --limit 10 --priority oldest

# Process AI-EWG linked videos first (best context)
ytseo generate --limit 10 --priority linked
```

**Priority Modes:**
- **recent** (default): Newest videos first - best for keeping current content optimized
- **oldest**: Oldest videos first - useful for backfilling entire catalog
- **linked**: Videos with `episode_id` first - prioritizes content with rich AI-EWG context

### 3. Targeted Video Processing

#### A. Fetch from YouTube and Process (NEW!)
```bash
# Fetch a specific video from YouTube and process immediately
ytseo fetch --video-id 1MvFqJqq4IA

# Video ID is from YouTube URL:
# https://www.youtube.com/watch?v=1MvFqJqq4IA
#                                 ^^^^^^^^^^^
```

**What happens:**
1. Fetches video metadata from YouTube API
2. Saves to local database
3. Immediately generates SEO suggestions
4. One command, complete workflow!

#### B. Process from Local Database
```bash
# Process a video already in your database
ytseo generate --video-id 1MvFqJqq4IA

# First, find the video ID
ytseo list --status pending
ytseo list --status suggested --limit 20
```

**Use Cases:**
- Pick any video from your channel without full sync
- Process new video immediately after upload
- Regenerate after prompt changes
- Fix bad suggestions
- Test with known content
- Debug specific videos

### 4. Status-Based Workflow
Videos progress through states:
```
pending → suggested → approved → applied
```

Only `pending` videos are processed by `generate`, preventing duplicate work.

## Recommended Workflows

### Daily Optimization (10-20 videos/day)
```bash
# Morning: Sync latest videos
ytseo sync --channel @TheNewsForum --limit 20

# Generate suggestions for newest content
ytseo generate --limit 10 --priority recent

# Review in Streamlit UI, approve best suggestions
ytseo ui

# Apply approved changes (with safety controls)
ytseo apply --limit 5
```

### Catalog Backfill (100s of videos)
```bash
# One-time: Sync entire catalog in batches
ytseo sync --channel @TheNewsForum --limit 100

# Process in daily batches
ytseo generate --limit 20 --priority oldest

# Or prioritize AI-EWG linked content
ytseo generate --limit 20 --priority linked
```

### AI-EWG Integration Priority
```bash
# Focus on videos with episode_id (richest context)
ytseo generate --limit 15 --priority linked
```

## Cost & Time Management

### LLM Call Estimates (per video)
- Title: ~100 tokens
- Description: ~500 tokens
- Tags: ~300 tokens
- Hashtags: ~100 tokens
- Thumbnail text: ~150 tokens
- Pinned comment: ~150 tokens

**Total: ~1,300 tokens/video (input + output)**

### Batch Recommendations
- **Small batches (5-10)**: Interactive testing, high-quality review
- **Medium batches (10-20)**: Daily optimization workflow
- **Large batches (20-50)**: Catalog backfill (review in Streamlit)

## Future Enhancements

### Phase 12: Analytics-Based Priority
```bash
# Process high-performing videos first
ytseo generate --priority popular --min-views 1000

# Process underperforming videos (SEO rescue)
ytseo generate --priority underperforming --max-views 500
```

### Smart Scheduling
- Cron job: Daily sync + generate (recent priority)
- Weekly: Backfill batch (oldest priority)
- Monthly: Re-optimize top performers

### Episode Mapping Intelligence
- Auto-link videos to AI-EWG episodes by title/date matching
- Prioritize unmapped videos for manual review
- Enrich context with episode transcripts

## Database Queries

### Check Processing Status
```sql
SELECT status, COUNT(*) 
FROM yt_videos 
GROUP BY status;
```

### Find Unprocessed Videos
```sql
SELECT video_id, title_original, published_at 
FROM yt_videos 
WHERE status='pending' 
ORDER BY published_at DESC 
LIMIT 20;
```

### Find AI-EWG Linked Videos
```sql
SELECT video_id, title_original, episode_id 
FROM yt_videos 
WHERE episode_id IS NOT NULL 
AND status='pending';
```
