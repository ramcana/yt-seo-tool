import os

from ytseo import db as dbmod


def test_db_init_and_query():
    conn = dbmod.connect(os.environ.get("DB_PATH", "data/ytseo.sqlite"))
    dbmod.apply_migrations(conn)
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='yt_videos'")
    row = cur.fetchone()
    assert row is not None
