# Multi-Channel Feature - Changelog

## Summary

Added support for managing multiple YouTube channels (@TheNewsForum and @ForumDailyNews) using a single OAuth authentication.

## Changes Made

### 1. Configuration (`.env`)
- ✅ Added `YOUTUBE_CHANNELS` environment variable
- ✅ Supports comma-separated list of channel handles
- ✅ Updated `.env.example` with multi-channel config

### 2. Core Library (`ytseo/`)
- ✅ **config.py**: Added `get_available_channels()` and `get_default_channel()` functions
- ✅ **models.py**: Updated `upsert_video()` to support `channel_handle` parameter with backward compatibility
- ✅ **workflows.py**: Updated `sync_channel()` to pass `channel_handle` when storing videos

### 3. Database Schema
- ✅ Created migration `0002_add_channel_handle.sql`
- ✅ Added `channel_handle` column to `yt_videos` table
- ✅ Added `channel_handle` column to `yt_channels` table
- ✅ Created index on `channel_handle` for faster filtering

### 4. Streamlit UI (`app/`)
- ✅ **shared.py**: New shared component with `render_channel_selector()`
- ✅ **main.py**: Added channel selector to main page
- ✅ **01_Dashboard.py**: Added channel selector and channel display
- ✅ **02_Video_List.py**: Added channel selector and "Sync Channel" feature
- ✅ **03_Video_Detail.py**: Added channel selector
- ✅ **04_Settings.py**: Enhanced with channel configuration display

### 5. Documentation
- ✅ **docs/multi_channel_setup.md**: Comprehensive guide for multi-channel setup
- ✅ **README.md**: Updated with multi-channel feature and config examples
- ✅ **CHANGELOG_multi_channel.md**: This file

## Key Features

### Channel Selector Dropdown
- Appears in sidebar on all Streamlit pages
- Persists selection across page navigation using session state
- Automatically populated from `YOUTUBE_CHANNELS` config

### Channel-Aware Syncing
- Videos are tagged with `channel_handle` when synced
- Each channel can be synced independently
- Database stores both YouTube `channel_id` and human-readable `channel_handle`

### Single OAuth for Multiple Channels
- No need for separate credentials per channel
- One `token.pickle` file works for all channels under the same Google account
- OAuth authenticates at account level, not channel level

## Usage

### Configure Channels
```bash
# In .env file
YOUTUBE_CHANNELS=@TheNewsForum,@ForumDailyNews
```

### Use in Streamlit
1. Launch UI: `ytseo ui --port 8502`
2. Select channel from dropdown in sidebar
3. Go to Video List → Sync Channel
4. Videos are fetched and tagged with channel handle

### Use in CLI
```bash
# Sync specific channel
ytseo sync --channel @ForumDailyNews --limit 20

# Generate suggestions (works with any channel's videos)
ytseo generate --limit 10
```

## Migration Path

### For Existing Users
1. Update `.env` with `YOUTUBE_CHANNELS`
2. Restart Streamlit UI
3. Run migration (automatic on next sync/UI launch)
4. Re-sync channels to populate `channel_handle` field

### Backward Compatibility
- Old databases without `channel_handle` column still work
- `upsert_video()` checks for column existence before using it
- Graceful fallback to old schema if migration hasn't run

## Testing Checklist

- [ ] Verify channel selector appears in all Streamlit pages
- [ ] Test syncing @TheNewsForum
- [ ] Test syncing @ForumDailyNews
- [ ] Verify videos are tagged with correct `channel_handle`
- [ ] Test channel switching in UI
- [ ] Verify session state persists across pages
- [ ] Test backward compatibility with old database schema

## Future Enhancements

- [ ] Filter dashboard metrics by selected channel
- [ ] Filter video list by channel
- [ ] Channel-specific analytics and reporting
- [ ] Bulk operations per channel
- [ ] Channel comparison views

## Files Modified

### Configuration
- `.env`
- `.env.example`

### Core Library
- `ytseo/config.py`
- `ytseo/models.py`
- `ytseo/workflows.py`

### Database
- `migrations/0002_add_channel_handle.sql` (new)

### Streamlit UI
- `app/shared.py` (new)
- `app/main.py`
- `app/pages/01_Dashboard.py`
- `app/pages/02_Video_List.py`
- `app/pages/03_Video_Detail.py`
- `app/pages/04_Settings.py`

### Documentation
- `README.md`
- `docs/multi_channel_setup.md` (new)
- `CHANGELOG_multi_channel.md` (new)

## Technical Notes

### Session State Management
The channel selector uses Streamlit's `st.session_state` to persist the selected channel across page navigation. This ensures a consistent user experience.

### Database Schema Evolution
The migration adds `channel_handle` as a nullable column, allowing existing videos to remain in the database. New syncs will populate this field.

### OAuth Scope
The existing YouTube Data API v3 scopes already grant access to all channels under the authenticated Google account. No scope changes needed.

## Support

For issues or questions:
1. Check `docs/multi_channel_setup.md` for detailed setup instructions
2. Verify `.env` configuration
3. Ensure channels are under the same Google account
4. Check that OAuth token has proper permissions
