## Why

The welcome page preview currently uses hardcoded placeholder strings (e.g. `'preview-mrs-green-apple'`) as artist IDs, causing `invalid_argument` validation errors because the Concert List RPC expects valid UUIDs. Additionally, artist UUIDs differ per environment (dev/staging/prod), so they cannot be embedded in source code.

## What Changes

- Replace the hardcoded `PREVIEW_ARTIST_IDS` string array with a runtime-resolved list read from the `VITE_PREVIEW_ARTIST_IDS` environment variable (comma-separated UUIDs)
- Remove Ano from the curated preview artist list
- Raise the minimum number of artists required to show the preview from 3 to 5
- Add `VITE_PREVIEW_ARTIST_IDS` to the frontend k8s ConfigMap for the dev environment with real UUIDs queried from the database

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `welcome-dashboard-preview`: Minimum artists with concerts raised from 3 to 5; artist list becomes environment-configurable (no longer hardcoded); Ano removed from curated list

## Impact

- **Frontend**: `src/constants/preview-artists.ts` — reads from `import.meta.env.VITE_PREVIEW_ARTIST_IDS`
- **Cloud Provisioning**: `k8s/overlays/dev/frontend/` ConfigMap — new `VITE_PREVIEW_ARTIST_IDS` key with dev UUIDs
- **No API changes** — uses existing `ConcertService/List` RPC
