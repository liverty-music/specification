## 1. Frontend: preview-artists.ts

- [x] 1.1 Read `VITE_PREVIEW_ARTIST_IDS` from `import.meta.env`, split by comma, and trim whitespace to produce the `PREVIEW_ARTIST_IDS` array
- [x] 1.2 Add a dev-only console warning when the env var is absent or empty
- [x] 1.3 Update `PREVIEW_MIN_ARTISTS_WITH_CONCERTS` from `3` to `5`
- [x] 1.4 Remove Ano from any inline comments or documentation in the file

## 2. Frontend: `.env` and `Dockerfile`

- [x] 2.1 Add `VITE_PREVIEW_ARTIST_IDS` to `frontend/.env` with the 11 dev UUIDs (comma-separated, no spaces): `019c8655-7a05-71ef-82b4-a4ac2494e29f,019c8655-7a05-721d-b0a8-4c11724d5c90,019c8655-7a05-71e9-9af5-e1cd4fbfd367,019c899e-baff-7ecd-8af2-e8dc819e29e4,019c8655-7a05-71f5-acd4-46157dcb0bec,019c8655-7a05-722a-bdae-a89596378f90,019c8655-7a05-72ff-8654-4e09e64043da,019c8655-7a05-723e-bef1-2d2433cd53f5,019c8655-7a05-7217-8f63-7a261ebcfceb,019c8655-7a05-72e7-a9c3-44a27d2bf07e,019c8655-7a05-71fc-bc48-92705b9ddb68`
- [x] 2.2 Remove the redundant `ARG VITE_VAPID_PUBLIC_KEY` and `ENV VITE_VAPID_PUBLIC_KEY=...` lines from `frontend/Dockerfile` (dead code — `.env` is already present in the build context)

## 3. Cleanup

- [x] 3.1 Delete the temporary debug pod `psql-debug` in the `backend` namespace
- [x] 3.2 Delete tmp files: `tmp/query_artists.sql`, `tmp/query_preview_artists.sql`, `tmp/query_all_preview.sql`, `tmp/run_query.sh`, `tmp/run_preview_query.sh`, `tmp/run_all_preview.sh`
