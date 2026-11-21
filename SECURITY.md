# Security policy

## Supported versions

Only the latest release of aio-grab and the `latest` Docker image get security fixes. Upgrade with
`pip install -U aio-grab` or `docker compose pull`.

## Reporting a vulnerability

Please **don't open a public issue** for a security problem. Report it privately through
[GitHub's private vulnerability reporting](https://github.com/fonneyx/Aio/security/advisories/new)
(the **Security** tab → **Report a vulnerability**).

Include what an attacker can do, the steps or a proof of concept, and the version you tested. You'll get a
reply within 7 days, and a fix or a plan within 30 days for confirmed issues. You'll be credited in the
release notes unless you'd rather not be.

## Scope

In scope: the aio-grab library and CLI, the web app and HTTP API, and the Docker image.

Bugs in yt-dlp, gallery-dl or ffmpeg belong to those projects; report them upstream. Aio picks up their
fixes when you upgrade.

## Running Aio safely

- **Set `AIO_AUTH`** before the web app is reachable from anything but your own machine. Without it, anyone who
  can reach the port can download through your server.
- **Anyone who can use the web app can make the server fetch any address it can reach**, including services
  on your local network. That's inherent to a downloader. Don't run Aio next to internal services that trust
  their network, and don't share access with people you don't trust.
- **If you connect a bot or another service to the API**, let only people you trust use it. Everyone who can
  use the bot downloads through your server and its IP address.
- **Protect your cookies file**: it is a logged-in session for that site.
- Put the web app behind HTTPS (a reverse proxy such as Caddy) when you use it over the internet, because
  Basic auth sends the password with every request.
