# yt-dlp-web-ui

## Reverse Proxy Configuration

If running the app behind a reverse proxy at a sub-path (e.g., `https://example.com/aio/`), ensure your configuration strips the sub-path if necessary or proxies to the root.

### Nginx Example
```nginx
location /aio/ {
    proxy_pass http://localhost:8000/;
    proxy_set_header Host $host;
}
```

### Caddy Example
```caddy
example.com {
    handle_path /aio/* {
        reverse_proxy localhost:8000
    }
}
```