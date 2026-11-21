from datetime import date

import pytest
from yt_dlp.utils import DownloadError

from aio_grab import Engine, engine
from aio_grab.freshness import NO_RUNTIME, is_stale, is_youtube, warnings, ytdlp_age_days


def test_age_comes_from_the_version_date():
    assert ytdlp_age_days(date(2026, 9, 18), "2026.08.19") == 30
    assert ytdlp_age_days(date(2026, 9, 18), "2026.08.19.233012") == 30  # nightly builds
    assert ytdlp_age_days(date(2026, 9, 18), "unknown") is None
    assert not is_stale(date(2026, 9, 18), "2026.08.19")
    assert is_stale(date(2026, 9, 19), "2026.08.19")


def test_youtube_hosts():
    assert is_youtube("https://youtu.be/x") and is_youtube("https://music.youtube.com/watch?v=x")
    assert not is_youtube("https://notyoutube.com/x") and not is_youtube("https://vimeo.com/1")


def test_status_warnings(monkeypatch):
    assert warnings({"node": {}}, today=date(2000, 1, 1)) == []
    assert warnings({}, today=date(2000, 1, 1)) == [NO_RUNTIME]


@pytest.fixture
def eng():
    return Engine(fetch_ffmpeg=False)


def test_unexplained_errors_get_the_likely_fix(eng, monkeypatch):
    eng.js_runtimes = {}
    monkeypatch.setattr(engine, "is_stale", lambda: True)
    monkeypatch.setattr(engine, "ytdlp_age_days", lambda: 45)
    message = str(eng._error(DownloadError("ERROR: [youtube] abc: Requested format is not available"),
                             "https://www.youtube.com/watch?v=abc"))
    assert message.startswith("Requested format is not available.")
    assert "JavaScript runtime" in message and "45 days old" in message

    elsewhere = str(eng._error(DownloadError("ERROR: something odd"), "https://vimeo.com/1"))
    assert "JavaScript" not in elsewhere and "45 days old" in elsewhere


def test_known_causes_stay_short(eng, monkeypatch):
    eng.js_runtimes = {}
    monkeypatch.setattr(engine, "is_stale", lambda: True)
    message = str(eng._error(DownloadError("ERROR: [youtube] abc: Private video"), "https://youtu.be/abc"))
    assert message == "This video is private."
