"""Is this install able to keep up with the sites? Most "it stopped working" reports come down to an old
yt-dlp or a missing JavaScript runtime, which YouTube needs to solve its playback challenges."""

import shutil
from datetime import date
from urllib.parse import urlsplit

import yt_dlp

# yt-dlp ships fixes every week or two; past this age, failures are likely to be fixed by an update.
STALE_DAYS = 30
JS_RUNTIMES = ("deno", "node", "bun")
YOUTUBE_HOSTS = ("youtube.com", "youtu.be", "youtube-nocookie.com")

UPDATE_HINT = "Update yt-dlp: pip install -U yt-dlp (Docker: docker compose pull)."
NO_RUNTIME = "YouTube needs a JavaScript runtime to download reliably. Install Node.js or Deno and try again."


def ytdlp_version() -> str:
    return yt_dlp.version.__version__


def ytdlp_age_days(today: date | None = None, version: str | None = None) -> int | None:
    """Days since the installed yt-dlp was released (its version is its release date), or None if unknown."""
    try:
        year, month, day = (int(part) for part in (version or ytdlp_version()).split(".")[:3])
        released = date(year, month, day)
    except ValueError:
        return None
    return max(0, ((today or date.today()) - released).days)


def is_stale(today: date | None = None, version: str | None = None) -> bool:
    age = ytdlp_age_days(today, version)
    return age is not None and age > STALE_DAYS


def find_js_runtimes() -> dict[str, dict]:
    """The JavaScript runtimes on PATH, in yt-dlp's js_runtimes option format."""
    return {name: {} for name in JS_RUNTIMES if shutil.which(name)}


def is_youtube(url: str) -> bool:
    host = (urlsplit(url).hostname or "").lower()
    return any(host == h or host.endswith("." + h) for h in YOUTUBE_HOSTS)


def warnings(js_runtimes: dict, today: date | None = None) -> list[str]:
    """Plain-language problems with this install, for status displays. Empty when all is well."""
    found = []
    if is_stale(today):
        found.append(f"yt-dlp is {ytdlp_age_days(today)} days old, and sites change often, so some downloads "
                     f"may fail. {UPDATE_HINT}")
    if not js_runtimes:
        found.append(NO_RUNTIME)
    return found
