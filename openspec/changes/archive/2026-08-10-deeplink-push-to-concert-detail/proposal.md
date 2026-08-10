## Why

Tapping a new-concert push notification currently lands the fan on an unfiltered `/dashboard`, forcing them to hunt for the concert they were just told about. Two defects compound: the backend sends a bare `/dashboard` URL (dropping the artist filter that the `dashboard-artist-filter` spec already requires — regressed when a prior `/concerts?artist=<id>` 404 was "fixed"), and the intended experience — land the fan directly on the concert that triggered their hype match — was never specified or built. The notification promises a specific concert for a specific artist; the destination should honor that promise.

## What Changes

- The new-concert push notification deep-link SHALL target the **earliest concert that matched the recipient's own hype level** (`/concerts/<concertId>`), not a bare dashboard.
- Tapping the notification SHALL **auto-open that concert's detail sheet** on the dashboard, with the dashboard **filtered to the concert's artist** behind it.
- The notification body count and the deep-link target SHALL both be computed from the **per-recipient hype-matched subset** of the newly created concerts. This fixes a pre-existing over-count where a `home`-hype fan saw the count of *all* new concerts rather than only those in their home area. **BREAKING** (behavioral): `home`-hype recipients now see a smaller, area-accurate count.
- The deep-link **reuses the existing `/concerts/:id` detail-sheet URL** (the sheet already writes it on open and reverts to `/dashboard` on close; `concerts/:id` already routes to the dashboard). No new URL surface, no redundant `?artists=` query param (the artist is derived from the opened concert), no new get-by-id RPC (the concert is guaranteed present in the dashboard's existing `listByFollower` result).
- When the target concert is genuinely absent from the fan's list (rare: unfollowed after send, or a zero-date / unresolved-performer data anomaly), the dashboard SHALL **degrade gracefully to the artist-filtered view** without opening a sheet.

## Capabilities

### New Capabilities
<!-- No new capabilities; all behavior extends existing specs. -->

### Modified Capabilities
- `push-notification-service`: the deep-link URL and the notification count SHALL be computed from the per-recipient hype-matched concert subset, and the deep-link SHALL point to the earliest concert in that subset (tie-broken by start time).
- `dashboard-artist-filter`: the push-notification deep-link requirement changes — the notification URL is now `/concerts/<concertId>` (not `/dashboard?artists=<id>`), and the artist filter is derived from the opened concert rather than carried in the URL.
- `concert-detail`: add a deep-link auto-open requirement — navigating to `/concerts/:id` (e.g. from a push notification) SHALL open that concert's detail sheet after the authoritative concert fetch resolves, filtered to the concert's artist, degrading to filter-only when the concert is absent.

## Impact

- **specification**: delta specs for the three capabilities above. No proto change expected — the Web Push payload already carries `data.url`, and the count is a formatting concern, not a schema field.
- **backend**: `internal/usecase/push_notification_uc.go` and the hype entity types — refactor the per-follower `ShouldNotify(...) bool` gate into a matched-subset selector, choose the earliest matched concert per recipient for `data.url`, and align the body count to that subset.
- **frontend**: `src/routes/dashboard/dashboard-route.ts` — read the `:id` route param in `loading()`, and after the existing `listByFollower` fetch resolves, open the detail sheet for that concert and derive the artist filter. No changes to the RPC layer or the detail-sheet component's own open/close.
- **Shipping goal**: land in prod — specification Release → BSR (only if a proto change proves necessary) → backend release → frontend release → prod pin bump → verify a real notification tap opens the correct concert sheet.
