# async_http_proxy

A small **asynchronous HTTP proxy** written in Python (`aiohttp`). Useful for local debugging, traffic inspection, and learning how proxies work.

> **Note:** HTTP only for now — HTTPS/CONNECT tunneling is not supported yet.

## Features

- Async request forwarding with `aiohttp`
- Docker and bare-metal run modes
- `/stats` endpoint (uptime, bytes transferred)
- Basic range-header handling
- Pytest suite for smoke checks
- Apache 2.0 license

## Quick start

### With Docker Compose

```bash
docker-compose up
# Proxy listens on http://localhost:8080
```

### With Python

```bash
pip install -r requirements.txt
HTTP_PROXY_PORT=8080 python3 proxy.py
```

## Use it

Point an app or browser at the proxy:

```bash
export http_proxy=http://localhost:8080
curl -x http://localhost:8080 http://example.com
```

Or set the HTTP proxy in Firefox / another browser that supports per-app proxies.

**Docker note:** if `HTTP_PROXY` is already set at the OS level, prefer running the proxy as a host Python process so the container is not affected by that setting.

## Stats

With the proxy running:

```text
http://localhost:8080/stats
```

Returns JSON with:

- `uptime`
- `bytes transferred` (and related counters)

## Tests

```bash
pip install -r test_requirements.txt
pytest tests.py
```

## Limitations

- No HTTPS / CONNECT support yet
- Intended for local/dev use, not as a hardened production edge proxy

## License

Apache 2.0 — see [LICENSE](LICENSE).

© Mohit Ranka
