-- Add channel_handle column to yt_videos for multi-channel support
-- This allows filtering videos by channel handle (@TheNewsForum, @ForumDailyNews, etc.)

ALTER TABLE yt_videos ADD COLUMN channel_handle TEXT;

-- Create index for faster channel filtering
CREATE INDEX IF NOT EXISTS idx_videos_channel_handle ON yt_videos(channel_handle);

-- Add channel_handle to yt_channels table as well
ALTER TABLE yt_channels ADD COLUMN channel_handle TEXT;
