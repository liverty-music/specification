# frontend-hosting Specification

## ADDED Requirements

### Requirement: Caddy SHALL serve `/config.json` with no-cache headers

The Caddy web server in the frontend container SHALL serve `/config.json` from the document root (`/srv/config.json`) with `Cache-Control: no-cache, no-store, must-revalidate` and `Content-Type: application/json; charset=utf-8` response headers. This ensures that ConfigMap updates (followed by pod rollout) propagate to clients on the next page load without depending on cache busting at the URL level.

#### Scenario: Caddyfile defines the /config.json header rule

- **WHEN** inspecting `frontend/Caddyfile`
- **THEN** a matcher SHALL be defined for `path /config.json`
- **AND** the matcher SHALL set `Cache-Control` to a value containing `no-cache`
- **AND** the matcher SHALL set `Content-Type` to `application/json; charset=utf-8` (the file extension default also produces JSON, but the explicit header guards against future mount-source changes)

#### Scenario: Live response carries the headers

- **WHEN** running `curl -I https://<env>.liverty-music.app/config.json` (or the apex for prod)
- **THEN** the response status SHALL be `200`
- **AND** the `Cache-Control` header SHALL contain `no-cache`
- **AND** the `Content-Type` header SHALL be `application/json` (charset suffix permitted)
