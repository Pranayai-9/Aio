<img src="server/aio_server/static/icons/icon-192.png" width="64" alt="" align="right">

# Aio

[![CI](https://github.com/fonneyx/Aio/actions/workflows/ci.yml/badge.svg)](https://github.com/fonneyx/Aio/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/aio-grab)](https://pypi.org/project/aio-grab/)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)

Aio downloads video, audio and images from a link. It works with YouTube and the
[1,000+ other sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) that yt-dlp supports, and it
uses gallery-dl for image galleries.

You can use it three ways:

- a self-hosted web app, which you can also install on your phone and use from the Share menu,
- a command-line tool and Python library, `aio-grab` on PyPI,
- a Telegram bot.

All three use the same library, so they offer the same options.

## Features

- Video up to 4K. AV1 or VP9 for the best picture, or H.264 for any device. HDR, MP4 or MKV, embedded subtitles.
- Audio as MP3, M4A, Opus, FLAC, WAV or the original stream, with cover art and tags.
- Images from photo posts, carousels and albums.
- Every quality with its codec and file size, shown before you download.
- Clips: download only `1:30` to `2:00`, for example.
- SponsorBlock, to cut sponsor segments from YouTube videos.
- No accounts and no tracking. The server deletes finished files after 24 hours.

## Quick start

Run the web app with Docker:

```bash
git clone https://github.com/fonneyx/Aio.git && cd Aio
docker compose up -d
```

Then open http://localhost:8000. The image includes ffmpeg and Node.js, which YouTube needs.

To use Aio from your phone, open the page on the phone and choose *Install app* or *Add to Home Screen*. Aio then
appears in the Share menu of other apps. The phone must reach your server, so set `AIO_AUTH` first
(see [Configuration](#configuration)).

To run the Telegram bot, add `AIO_TELEGRAM_TOKEN` from [@BotFather](https://t.me/BotFather) to `.env` and run
`docker compose --profile bot up -d`. The bot answers nobody until you add your Telegram ID to `AIO_TELEGRAM_USERS`.
Send it a message and it replies with your ID.

## Command line

```bash
pip install aio-grab
```

```bash
aio-grab https://youtu.be/dQw4w9WgXcQ           # best video, up to 4K
aio-grab -q 1080 --compatible URL               # 1080p H.264, plays on any device
aio-grab -x URL                                 # MP3, 320 kbps
aio-grab -x -f flac URL                         # lossless audio
aio-grab --start 1:30 --end 2:00 URL            # only that part
aio-grab -i URL                                 # list qualities and sizes, download nothing
aio-grab -a links.txt -o ~/Downloads            # one link per line
```

Aio uses the ffmpeg on your PATH. If there is none, it downloads a static build on first use.
For YouTube, install [Node.js](https://nodejs.org) or [Deno](https://deno.com).

## Python library

```python
import aio_grab

info = aio_grab.probe("https://youtu.be/dQw4w9WgXcQ")
print(info["title"], [row["label"] for row in info["video"]])   # ... ['4K', '1440p', '1080p', ...]

files = aio_grab.download("https://youtu.be/dQw4w9WgXcQ", "downloads", kind="audio", audio_format="mp3")
```

For cookies, a proxy or progress updates, create an `Engine`. One `Engine` can run many downloads at the same time.
The [library README](core/README.md) lists every option.

## Configuration

The server reads `AIO_*` environment variables from `.env` (Docker) or `server/.env` (from source).
[`.env.example`](.env.example) lists them all.

| Variable | Purpose | Default |
|---|---|---|
| `AIO_AUTH` | `user:password` for a login. Set it before other devices can reach the server. | none |
| `AIO_TELEGRAM_TOKEN` | Telegram bot token | none |
| `AIO_TELEGRAM_USERS` | Telegram user IDs that can use the bot, comma-separated. `*` allows everyone (not recommended). | nobody |
| `AIO_COOKIES_FILE` | Netscape `cookies.txt` for content that needs a login | none |
| `AIO_PROXY` | Proxy for requests to the sites | none |
| `AIO_WORKERS` | Downloads that run at the same time | `2` |
| `AIO_FILE_TTL_HOURS` | Hours before a finished file is deleted | `24` |
| `AIO_HOST`, `AIO_PORT` | Listen address | `127.0.0.1`, `8000` (Docker: `0.0.0.0`) |
| `AIO_STORAGE_DIR` | Folder for finished files | `server/storage` (Docker: `/data`) |
| `AIO_FFMPEG` | ffmpeg binary or folder | PATH, then a static build |

## HTTP API

The web app uses a small JSON API. You can call it from scripts too. Interactive docs are at `/docs`.

| Endpoint | Result |
|---|---|
| `POST /api/probe` `{"url": ...}` | Title, thumbnail, each resolution with codec and size, audio and subtitles. `kind` is `media`, `post` or `images`. |
| `POST /api/jobs` | Starts a download and returns `202` with a job ID. Takes the same options as the library's `Request`. |
| `GET /api/jobs/{id}` | `status`, `stage`, `progress`, `speed`, `eta`, `download_url` and `error` |
| `GET /api/jobs/{id}/file` | The finished file. Posts and galleries come as one ZIP. |
| `GET /api/health` | Versions, the age of yt-dlp, the JavaScript runtimes found, and any warnings |

## Limitations

- Aio downloads posts and playlists of up to 20 items. It does not download whole channels or long playlists yet
  ([#12](https://github.com/fonneyx/Aio/issues/12)).
- Jobs are kept in memory. A restart of the server forgets them and deletes their files.
- Some content needs a login. Export your browser's cookies to `cookies.txt` and set `AIO_COOKIES_FILE`.
- Sites change often. When a site stops working, update yt-dlp: `pip install -U aio-grab yt-dlp` or
  `docker compose pull`. The Docker image gets the newest yt-dlp every week, and the web app warns you when
  yt-dlp is more than 30 days old.

## Responsible use

Use Aio for content that you have the right to keep: your own uploads, Creative Commons and public-domain media,
or personal copies where the law allows them. Obey copyright law and the terms of each platform. Run Aio for
yourself, not as a public service.

You are responsible for what you download. Aio is not affiliated with YouTube, Instagram, TikTok or any other
platform. Their names only show which sites work. The software comes without warranty, as the
[license](LICENSE) states.

## Privacy

Aio has no analytics or telemetry and sends nothing to its authors. It connects only to the sites you download
from, to Telegram if you run the bot, and to GitHub once to get ffmpeg if none is installed.

The server log contains every link that it downloads, so keep the log private. A cookies file gives access to your
account on that site, so protect it like a password. If other people use your server, you are responsible for
their data under the privacy laws that apply to you.

## Development

You need Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --all-packages
uv run pytest
uv run aio-server        # web app on http://127.0.0.1:8000
```

`core/` is the `aio-grab` library and CLI. `server/` is the web app, the HTTP API and the Telegram bot.
[CONTRIBUTING.md](CONTRIBUTING.md) explains how to report a broken link and how to send a change.
To report a security problem, see [SECURITY.md](SECURITY.md).

## License

[GPL-3.0](LICENSE). Aio uses yt-dlp ([Unlicense](https://github.com/yt-dlp/yt-dlp/blob/master/LICENSE)),
gallery-dl ([GPL-2.0](https://github.com/mikf/gallery-dl/blob/master/LICENSE), which runs as a separate process)
and ffmpeg (LGPL/GPL, a separate program). The Geist fonts in the web app use the
[SIL Open Font License](server/aio_server/static/fonts/OFL.txt).
