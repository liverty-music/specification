## Context

The Welcome page fetches live concert data for a curated artist list to render a read-only dashboard preview. The list was implemented as a hardcoded TypeScript array of placeholder slug strings (`'preview-mrs-green-apple'`, etc.). These strings are not valid UUIDs, causing the backend's `ConcertService/List` RPC to reject every request with `invalid_argument: artist_id.value: value must be a valid UUID`.

Artist UUIDs are assigned at seed/migration time and differ between environments (dev, staging, prod), so they cannot safely be embedded in source code. The fix is to move the list to an environment variable resolved at build time via Vite's `import.meta.env`.

Current dev UUIDs (queried from the dev DB via k8s pod):

| Artist | UUID |
|---|---|
| Mrs. GREEN APPLE | `019c8655-7a05-71ef-82b4-a4ac2494e29f` |
| YOASOBI | `019c8655-7a05-721d-b0a8-4c11724d5c90` |
| Vaundy | `019c8655-7a05-71e9-9af5-e1cd4fbfd367` |
| SUPER BEAVER | `019c899e-baff-7ecd-8af2-e8dc819e29e4` |
| King Gnu | `019c8655-7a05-71f5-acd4-46157dcb0bec` |
| Official髭男dism | `019c8655-7a05-722a-bdae-a89596378f90` |
| Creepy Nuts | `019c8655-7a05-72ff-8654-4e09e64043da` |
| Ado | `019c8655-7a05-723e-bef1-2d2433cd53f5` |
| back number | `019c8655-7a05-7217-8f63-7a261ebcfceb` |
| ONE OK ROCK | `019c8655-7a05-72e7-a9c3-44a27d2bf07e` |
| RADWIMPS | `019c8655-7a05-71fc-bc48-92705b9ddb68` |

(Ano removed from the list per product decision.)

## Goals / Non-Goals

**Goals:**
- Fix the `invalid_argument` UUID validation error on the Welcome page
- Make the preview artist list configurable per environment without code changes
- Remove Ano from the curated list
- Raise the minimum displayable artists from 3 to 5

**Non-Goals:**
- Dynamic/runtime configuration (admin UI, feature flags, remote config)
- Staging or prod UUID configuration (out of scope for this change)
- Changing the Welcome page UI or the RPC interface

## Decisions

### Decision: Comma-separated single env var (`VITE_PREVIEW_ARTIST_IDS`)

**Chosen:** One `VITE_PREVIEW_ARTIST_IDS` env var with comma-separated UUIDs.

**Alternatives considered:**
- Individual env vars per artist (`VITE_PREVIEW_ARTIST_ID_MRS_GREEN_APPLE`, ...): Verbose, brittle to rename, and each artist addition requires a config change + code change. Rejected.
- Remote config / feature flags: Overly complex for a static curated list. Rejected.

The comma-separated approach allows the list to be changed per environment purely via ConfigMap without touching TypeScript source.

### Decision: Parse at module load time in `preview-artists.ts`

`VITE_PREVIEW_ARTIST_IDS` is split and trimmed once when the module is imported. This keeps all preview-artist logic in one file and avoids repeated parsing at render time.

### Decision: `.env` file (not k8s ConfigMap)

All other frontend env vars (`VITE_API_BASE_URL`, `VITE_ZITADEL_*`, `VITE_VAPID_PUBLIC_KEY`) are managed via a committed `.env` file at the repo root. `VITE_PREVIEW_ARTIST_IDS` follows the same pattern.

**Why not k8s ConfigMap:** Vite replaces `import.meta.env.*` at Docker build time — by the time the container starts, all `VITE_*` values are already baked into the JS bundle. A ConfigMap injected as a container env var has no effect on Vite output. The frontend k8s overlay contains no ConfigMap; all build-time config lives in `.env`.

**Why not GitHub Actions env vars / build-args:** The existing `ARG VITE_VAPID_PUBLIC_KEY` in the Dockerfile is redundant — the `.env` file is COPYed into the build context and Vite reads it directly. No build-arg plumbing is needed.

### Decision: Remove redundant `ARG`/`ENV` from Dockerfile

`ARG VITE_VAPID_PUBLIC_KEY` / `ENV VITE_VAPID_PUBLIC_KEY=...` in the Dockerfile is dead code since `.env` is already present in the build context. Remove it to avoid misleading future readers.

## Risks / Trade-offs

- **Build-time bake-in**: Vite replaces `import.meta.env.*` at build time. The Docker image contains the UUIDs from `.env` at the time of the build. This is acceptable; dev/staging/prod have separate CI builds and separate `.env` files.
  → Mitigation: Document in `.env` that UUIDs must be updated when artists are re-seeded.

- **Empty env var**: If `VITE_PREVIEW_ARTIST_IDS` is unset or empty, the preview silently shows nothing (falls below the minimum threshold). No crash.
  → Mitigation: Add a fallback empty array with a dev-only console warning.

## Migration Plan

1. Add `VITE_PREVIEW_ARTIST_IDS` to `frontend/.env` with the 11 dev UUIDs.
2. Update `preview-artists.ts` to read from `import.meta.env.VITE_PREVIEW_ARTIST_IDS`.
3. Update `PREVIEW_MIN_ARTISTS_WITH_CONCERTS` from `3` to `5`.
4. Remove the redundant `ARG VITE_VAPID_PUBLIC_KEY` / `ENV` lines from `Dockerfile`.
5. Merge PR — next CI build picks up the new `.env` value.

No rollback complexity: reverting the PR restores the old placeholder strings (which were already broken).
