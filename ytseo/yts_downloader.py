from __future__ import annotations

from pathlib import Path
from typing import Optional


def download(video_id: str, out_dir: str = "downloads") -> Optional[Path]:
    try:
        from yt_dlp import YoutubeDL  # type: ignore
    except Exception:
        return None

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    url = f"https://www.youtube.com/watch?v={video_id}"
    outtmpl = str(Path(out_dir) / "%(id)s.%(ext)s")
    ydl_opts = {"outtmpl": outtmpl, "format": "mp4/bestaudio/best"}
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return Path(out_dir)
