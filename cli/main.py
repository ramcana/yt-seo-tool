from __future__ import annotations

import subprocess
from typing import Optional

import typer

from ytseo import db as dbmod
from ytseo import models
from ytseo import workflows
from ytseo import seo_engine
from ytseo import youtube_api
from ytseo import yts_downloader
import json

app = typer.Typer(help="YT SEO Tool CLI")


@app.command()
def sync(channel: str = typer.Option(..., "--channel", help="Channel handle, e.g. @TheNewsForum"),
         limit: int = typer.Option(20, "--limit", help="Max number of videos to process")) -> None:
    """Fetch latest videos and update local database."""
    count = workflows.sync_channel(channel, limit=limit)
    typer.echo(f"[sync] channel={channel} fetched={count}")


@app.command()
def generate(
    limit: int = typer.Option(10, "--limit", help="Max number of pending videos to generate SEO for"),
    priority: str = typer.Option("recent", "--priority", help="Processing priority: recent|oldest|linked")
) -> None:
    """Generate SEO suggestions for pending videos using LLM."""
    created = workflows.generate_suggestions(limit=limit, priority=priority)
    typer.echo(f"[generate] created_suggestions={created} priority={priority}")


@app.command()
def apply(limit: int = typer.Option(10, "--limit", help="Max number of approved videos to apply")) -> None:
    """Apply approved metadata to YouTube (stubbed API)."""
    conn = dbmod.connect()
    dbmod.apply_migrations(conn)
    vids = models.get_videos_by_status(conn, status="approved", limit=limit)
    applied = 0
    for v in vids:
        success = youtube_api.update_video_metadata(v["video_id"], {"title": "Demo"})
        if success:
            conn.execute(
                "INSERT INTO yt_video_applied_changes(video_id, diff_json, applied_at) VALUES(?, ?, datetime('now'))",
                (v["video_id"], json.dumps({"applied": True})),
            )
            models.mark_video_status(conn, v["video_id"], "applied")
            applied += 1
    conn.commit()
    typer.echo(f"[apply] applied={applied}")


@app.command(name="list")
def list_cmd(status: Optional[str] = typer.Option(None, "--status", help="Filter by status: pending|suggested|approved|applied")) -> None:
    """List videos by status."""
    conn = dbmod.connect()
    dbmod.apply_migrations(conn)
    vids = models.get_videos_by_status(conn, status=status, limit=50)
    for v in vids:
        typer.echo(f"{v['video_id']} | {v.get('published_at','')} | {v.get('status','')}: {v.get('title_original','')}")


@app.command()
def download(video_id: str = typer.Option(..., "--video-id", help="YouTube video ID")) -> None:
    """Download audio/video for a video."""
    out = yts_downloader.download(video_id)
    typer.echo(f"[download] saved to: {out}")


@app.command()
def ui(port: int = typer.Option(8502, "--port", help="Streamlit port")) -> None:
    """Run the Streamlit UI."""
    import sys
    from pathlib import Path
    
    # Use python -m streamlit to ensure it uses the current environment
    cmd = [sys.executable, "-m", "streamlit", "run", "app/main.py", "--server.port", str(port)]
    typer.echo(f"[ui] launching: {' '.join(cmd)}")
    subprocess.run(cmd, check=False)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
