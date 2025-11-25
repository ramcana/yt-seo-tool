from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

try:  # Python 3.11+
    import tomllib as _toml
except Exception:  # Python <3.11
    try:
        import tomli as _toml  # type: ignore
    except Exception:  # Fallback no-TOML
        _toml = None  # type: ignore


_TOML_CACHE: Dict[str, Any] | None = None


def _load_toml_config() -> Dict[str, Any]:
    global _TOML_CACHE
    if _TOML_CACHE is not None:
        return _TOML_CACHE

    cfg_paths = [
        os.environ.get("YTSEO_CONFIG", "config/settings.toml"),
        "config/settings.example.toml",
    ]
    data: Dict[str, Any] = {}
    for p in cfg_paths:
        path = Path(p)
        if path.exists() and _toml is not None:
            try:
                data = _toml.loads(path.read_text(encoding="utf-8"))  # type: ignore[attr-defined]
                break
            except Exception:
                pass
    _TOML_CACHE = data
    return data


def get_setting(key: str, default: Optional[Any] = None) -> Any:
    val = os.environ.get(key)
    if val is not None:
        return val
    cfg = _load_toml_config()
    return cfg.get(key, default)


def get_available_channels() -> list[str]:
    """Get list of available YouTube channels from config."""
    channels_str = get_setting("YOUTUBE_CHANNELS", "")
    if not channels_str:
        # Fallback to default channel
        default = get_setting("DEFAULT_CHANNEL_HANDLE", "@TheNewsForum")
        return [default] if default else []
    
    # Parse comma-separated list and strip whitespace
    channels = [ch.strip() for ch in channels_str.split(",") if ch.strip()]
    return channels if channels else ["@TheNewsForum"]


def get_default_channel() -> str:
    """Get the default channel (first in list or DEFAULT_CHANNEL_HANDLE)."""
    channels = get_available_channels()
    return channels[0] if channels else "@TheNewsForum"
