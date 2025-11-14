-- Initial schema for yt-seo-tool

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS yt_channels (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  channel_id TEXT UNIQUE,
  title TEXT,
  last_synced TEXT
);

CREATE TABLE IF NOT EXISTS yt_videos (
  video_id TEXT PRIMARY KEY,
  channel_id TEXT,
  title_original TEXT,
  description_original TEXT,
  tags_original TEXT,
  published_at TEXT,
  episode_id TEXT,
  status TEXT
);

CREATE TABLE IF NOT EXISTS yt_video_suggestions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  video_id TEXT,
  language_code TEXT,
  title TEXT,
  description TEXT,
  tags_json TEXT,
  hashtags_json TEXT,
  thumbnail_text TEXT,
  pinned_comment TEXT,
  playlists_json TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS yt_video_applied_changes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  video_id TEXT,
  diff_json TEXT,
  applied_at TEXT
);

CREATE TABLE IF NOT EXISTS yt_language_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT,
  label TEXT,
  enabled INTEGER
);

CREATE TABLE IF NOT EXISTS yt_sync_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_date TEXT,
  count_fetched INTEGER,
  notes TEXT
);
