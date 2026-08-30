## 1. Specification (proto)

- [x] 1.1 `entity/v1/media.proto`: new `Media` (`MediaId id`, `MediaKind kind`, `MediaAttributes attributes`) mirroring the DB `media` row; `MediaKind` enum 1:1 with the PG `media_kind` ENUM (`IMAGE` only); `MediaAttributes` = flat all-optional **read projection** carrying `Url thumb` + `Url large` for IMAGE (future `poster`/`stream`/`duration`/`youtube_video_id` appended); kind-gated protovalidate CEL (`kind == IMAGE ⇒ thumb, large set`); `MediaId` wrapper VO (UUID-format protovalidate; UUIDv7 is a server-minting convention, not a proto rule). Variant URLs are server-composed at read time, NOT persisted (design D6)
- [x] 1.2 `entity/v1/series.proto` (**BREAKING**): rename field 7 `cover_image` → `media`, retype `Url` → `entity.v1.Media`, `reserved "cover_image"` for the old name
- [x] 1.3 `rpc/organizer/v1/concert_service.proto` (**BREAKING**): remove the shipped `UploadCoverImage`; add `CreateMediaUploadURL` (req: content_type → resp: upload_url `Url`, media_id `MediaId`, max_bytes) + `AttachMedia` (req: series_id, media_id → empty resp: the image is not yet live, so nothing meaningful to return) with protovalidate + error docs; keep other verbs
- [x] 1.4 `MEDIA.uploaded` event payload contract (`{ media_id, series_id }` — `series_id` lets the consumer own the `series_media` cut-over, see 4.5) documented alongside existing event data
- [ ] 1.5 `buf lint`/`format`/`breaking` (add `buf skip breaking` label for the intentional break); spec PR merge → Release → BSR gen

## 2. Cloud-provisioning

- [ ] 2.1 New `organizer-media-internal` bucket (PRIVATE, no LB/CDN, uniform bucket-level access) for uploaded originals at `{org}/{mediaId}`: CORS allow `PUT` from the organizer Web App origin (dev localhost:9100 + `organizer.dev.…`; prod `organizer.…`), response headers `Content-Type`, `x-goog-content-length-range`. The served `organizer-media` bucket is unchanged (keeps `cdn/` prefix + LB). Two-bucket split (not an `internal/` prefix) so the served bucket's URL map never exposes originals — see design D5
- [ ] 2.2 media-processor image: Artifact Registry repo/entry for the new consumer image (backend `cmd/job`), prod immutable-tag policy consistent with existing repos
- [ ] 2.3 Workload Identity: `media-processor` GSA + WI binding — bucket-scoped `objectAdmin` on **both** buckets: read/delete on `organizer-media-internal` (originals) + write on `organizer-media` (`cdn/` variants); no project-level storage role
- [ ] 2.4 KEDA `ScaledJob` (`scaledobject.yaml`) triggered on JetStream `MEDIA.uploaded` (durable `media_uploaded`): resource requests/limits sized for libvips, `maxReplicaCount`, `backoffLimit`, spot nodeSelector (dev), `restartPolicy: Never`
- [ ] 2.5 `kubectl kustomize` dry-run for the new Job overlay(s) (dev + prod) — resources set, spot nodeSelector, no empty `resources: {}`

## 3. Backend — API (upload/attach)

- [ ] 3.1 GCS storer: add `SignedPutURL(bucket, key, contentType, maxBytes, ttl)` (V4, keyless via IAM SignBlob; `x-goog-content-length-range` condition) and **restore** a prefix-delete (`DeletePrefix`) for reclaim
- [ ] 3.2 `CreateMediaUploadURL` usecase + handler: **org-scoped auth** (caller is an organizer; no series is referenced yet), validate content type (JPEG/PNG/WebP), mint `mediaId` (UUIDv7), return signed `PUT` URL for `internal/{org}/{mediaId}` (15-min TTL) + `mediaId` + `max_bytes` (the single-source byte limit the client echoes as `x-goog-content-length-range`; matches the signed-URL condition)
- [ ] 3.3 `AttachMedia(series_id, media_id)` usecase + handler: **verify the caller OWNS `series_id`** (represented-artist ownership, not merely org-scoped — deny non-owners without revealing existence), INSERT the `media` row (idempotent per `media_id`), publish `MEDIA.uploaded { media_id, series_id }`, return empty. Do NOT re-point `series_media` here and do NOT delete the previous image's prefix — the **consumer owns the `series_media` cut-over** and reclaims the old prefix after writing the new variants (see 4.5), so an already-published concert keeps serving its old image with no 404 window
- [ ] 3.4 Remove the shipped `UploadCoverImage` handler/usecase/mapper path; mapper returns `Media { kind, attributes }` where `attributes.thumb`/`attributes.large` are composed per exposure from `{ORGANIZER_MEDIA_CDN_BASE}/cdn/{org}/{mediaId}/{variant}.webp` (via the media/series_media join)
- [ ] 3.5 `MEDIA` stream in `streams.go` (+ KEDA trigger already in 2.4); DI wiring
- [ ] 3.6 Unit tests: signed-URL issuance (type/size constraints), `AttachMedia` series-ownership reject (non-owner denied), attach idempotency, mapper variant URLs; `make check` with upgraded BSR

## 4. Backend — media-processor consumer (`cmd/job`)

- [ ] 4.1 Introduce libvips (govips) dependency; `cmd/job` build target + Dockerfile for the media-processor image
- [ ] 4.2 `MediaConsumer` (behavior `media_uploaded`): pull message → load `media` row → read `internal/{org}/{mediaId}`
- [ ] 4.3 Safety: magic-byte validation + header-first pixel/edge limit (≈50 MP / 8000 px) rejected **before** full decode; reject SVG/other
- [ ] 4.4 Processing: strip EXIF, encode WebP `thumb` (~800w) + `large` (~1920w), aspect preserved (no crop), immutable `Cache-Control`; write `cdn/{org}/{mediaId}/{variant}.webp`
- [ ] 4.5 On success: write new variants → **cut over in one transaction**: upsert `series_media(series_id)` → the new `media_id`, capturing the old `media_id` first if a row existed → **then** reclaim the previous image's `cdn/{org}/{old}/` prefix + delete the old `media` row (deferred until here so an already-published concert keeps serving its old variants until the replacement is ready) → delete the `internal/` original → ack. Transient failure = nak (`max_deliver=3`). Permanent failure (invalid image) = `term` + **delete the `internal/` original** (so failed uploads do not linger) + log/metric (reuse poison-consumer pattern). Idempotent on redelivery: deterministic variant overwrite, cut-over upsert is a no-op if already done, old-prefix/original deletes are no-ops if already gone
- [ ] 4.6 Unit/integration tests: valid image → variants + EXIF removed; oversized-dimension rejected pre-decode; invalid bytes → no variants + term + original deleted; replace = new variants written **and** `series_media` cut over to the new media **before** the old prefix/row are reclaimed (no 404 window); first upload = `series_media` inserted by the consumer; idempotent reprocess

## 5. Frontend (organizer console)

- [ ] 5.1 Image upload rework: `CreateMediaUploadURL` → direct `PUT` to GCS (Content-Type + `x-goog-content-length-range` headers) → `AttachMedia`
- [ ] 5.2 Client-side pre-check (type/size/dimensions) for UX (not security); optimistic **local blob** preview during/after upload
- [ ] 5.3 Render `media` as `Media` variants (thumb in lists, large in detail); 404-graceful until processed; re-upload path when an image never appears
- [ ] 5.4 `make check` with upgraded BSR

## 6. Observability

- [ ] 6.1 Metrics: processing latency, success/failure counts, JetStream `MEDIA.uploaded` pending/lag; alert on sustained failures or queue backlog (GMP/PromQL AlertPolicy consistent with existing consumer alerts)

## 7. Release & ship to prod

- [ ] 7.1 Backend PR merged → release → prod pin bump (API + media-processor image)
- [ ] 7.2 Cloud-provisioning PR merged → dev auto `pulumi up`; prod `pulumi up` (Console) — CORS, WI SA, KEDA ScaledJob, media-processor
- [ ] 7.3 Frontend PR merged → release (this is the first prod release of the authoring media UI — see organizer-event-authoring 5.2, which now ships via this pipeline)
- [ ] 7.4 Verify in prod: organizer uploads an image for an owned draft → processed WebP `thumb`/`large` served over `https://media.…/cdn/{org}/{mediaId}/…` (EXIF removed); replace reclaims old variants; a malformed/oversized-dimension image yields no variants; publish is independent of processing
