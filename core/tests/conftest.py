import pytest

from aio_grab import engine


@pytest.fixture(autouse=True)
def fresh_ytdlp(monkeypatch):
    """Tests must not depend on how old the installed yt-dlp is today."""
    monkeypatch.setattr(engine, "is_stale", lambda: False)
