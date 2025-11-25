# Multi-Channel Setup Guide

This guide explains how to manage multiple YouTube channels with the same OAuth credentials.

## Overview

The yt-seo-tool now supports managing multiple YouTube channels under the same Google account. You can:
- Switch between channels using a dropdown in the Streamlit UI
- Sync videos from different channels
- Filter and view data per channel
- Use the same OAuth tokens for all channels

## Configuration

### 1. Update `.env` File

Add your channels to the `YOUTUBE_CHANNELS` variable (comma-separated):

```bash
# Multiple channels (comma-separated, first is default)
YOUTUBE_CHANNELS=@TheNewsForum,@ForumDailyNews

# This is used as fallback if YOUTUBE_CHANNELS is not set
DEFAULT_CHANNEL_HANDLE=@TheNewsForum
```

### 2. OAuth Authentication

**You do NOT need separate credentials for each channel!**

Your existing OAuth setup works for all channels under the same Google account:
- `config/client_secret.json` - Single OAuth client (shared)
- `token.pickle` - Single token file (shared)

The OAuth token authenticates at the **Google Account level**, granting access to all channels managed by that account.

## Using Multiple Channels

### In Streamlit UI

1. **Launch the UI:**
   ```bash
   ytseo ui --port 8502
   ```

2. **Select Channel:**
   - Look for the "📺 Channel" dropdown in the sidebar
   - Select the channel you want to work with
   - The selection persists across page navigation

3. **Sync Channel:**
   - Go to "Video List" page
   - Expand "🔄 Sync Channel from YouTube"
   - Click "Sync Channel" to fetch videos from the selected channel

### Via CLI

You can still use the CLI with the `--channel` flag:

```bash
# Sync @TheNewsForum
ytseo sync --channel @TheNewsForum --limit 20

# Sync @ForumDailyNews
ytseo sync --channel @ForumDailyNews --limit 20

# Generate suggestions for specific channel videos
ytseo generate --limit 10 --priority recent
```

## Database Schema

Videos are now tagged with `channel_handle` for filtering:

```sql
-- Migration 0002_add_channel_handle.sql
ALTER TABLE yt_videos ADD COLUMN channel_handle TEXT;
CREATE INDEX idx_videos_channel_handle ON yt_videos(channel_handle);
```

The migration runs automatically when you sync or use the app.

## Features

### Channel Selector Component

Located in `app/shared.py`, the channel selector:
- Reads available channels from `YOUTUBE_CHANNELS` config
- Stores selection in Streamlit session state
- Displays in sidebar on all pages
- Auto-refreshes when selection changes

### Channel-Aware Syncing

When you sync a channel:
1. Videos are fetched from YouTube API
2. Each video is tagged with the `channel_handle`
3. Database stores both `channel_id` (YouTube ID) and `channel_handle` (@name)

### Filtering (Coming Soon)

Future updates will add:
- Dashboard metrics filtered by selected channel
- Video list filtered by channel
- Channel-specific analytics

## Adding a New Channel

1. **Ensure the channel is under the same Google account**
   - Both channels must be managed by the account that authenticated the OAuth token

2. **Add to `.env`:**
   ```bash
   YOUTUBE_CHANNELS=@TheNewsForum,@ForumDailyNews,@NewChannel
   ```

3. **Restart Streamlit:**
   ```bash
   ytseo ui --port 8502
   ```

4. **Sync the new channel:**
   - Select the channel from dropdown
   - Click "Sync Channel"

## Troubleshooting

### "Channel not found" error

**Cause:** The channel handle might be incorrect or not accessible.

**Solution:**
1. Verify the channel handle (e.g., `@ForumDailyNews`)
2. Check that the channel is public or managed by your Google account
3. Try syncing with a smaller limit first: `ytseo sync --channel @ChannelName --limit 5`

### OAuth permission errors

**Cause:** Token doesn't have access to the channel.

**Solution:**
1. Delete `token.pickle`
2. Re-run OAuth flow: `ytseo sync --channel @YourChannel --limit 5`
3. Ensure you authenticate with the Google account that manages all channels

### Channels not appearing in dropdown

**Cause:** `YOUTUBE_CHANNELS` not set in `.env`

**Solution:**
1. Check `.env` file has `YOUTUBE_CHANNELS=@Channel1,@Channel2`
2. Restart Streamlit UI
3. Verify no typos in channel handles

## Architecture

```
┌─────────────────────────────────────────┐
│  Google Account (OAuth)                 │
│  ├── @TheNewsForum                      │
│  └── @ForumDailyNews                    │
└─────────────────────────────────────────┘
              │
              │ Single OAuth Token
              ▼
┌─────────────────────────────────────────┐
│  yt-seo-tool                            │
│  ├── config/client_secret.json          │
│  ├── token.pickle                       │
│  └── .env                               │
│      └── YOUTUBE_CHANNELS=@Chan1,@Chan2 │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Streamlit UI                           │
│  └── Channel Selector Dropdown          │
│      ├── @TheNewsForum                  │
│      └── @ForumDailyNews                │
└─────────────────────────────────────────┘
```

## Best Practices

1. **Keep channel list updated** - Add new channels to `.env` as you onboard them
2. **Use descriptive handles** - Always use the @ format (e.g., `@TheNewsForum`)
3. **Sync regularly** - Each channel should be synced independently
4. **Monitor both channels** - Use the dashboard to track optimization progress per channel

## Related Files

- `ytseo/config.py` - Channel configuration parsing
- `app/shared.py` - Channel selector component
- `ytseo/workflows.py` - Channel-aware sync logic
- `ytseo/models.py` - Database operations with channel_handle
- `migrations/0002_add_channel_handle.sql` - Schema update
