> **As-built note (`declarative-jetstream-nack`, shipped 2026-09-01).** The
> completed §2–§4 tasks below say `media-processor` / KEDA `ScaledJob` / `cmd/job`
> — the form originally shipped. That was reworked by `declarative-jetstream-nack`:
> `media-processor` → a long-running **`media-consumer`** Deployment behind a
> scale-to-zero **`ScaledObject`**, consuming the **NACK-owned pull** durable
> `media_uploaded` (the app no longer creates durables). Those task texts are kept
> as the historical record; the design/proposal reflect the current end state.

## 1. Specification (proto)

- [x] 1.1 `entity/v1/media.proto`: new `Media` (`MediaId id`, `MediaKind kind`, `MediaAttributes attributes`) mirroring the DB `media` row; `MediaKind` enum 1:1 with the PG `media_kind` ENUM (`IMAGE` only); `MediaAttributes` = flat all-optional **read projection** carrying `Url thumb` + `Url large` for IMAGE (future `poster`/`stream`/`duration`/`youtube_video_id` appended); kind-gated protovalidate CEL (`kind == IMAGE ⇒ thumb, large set`); `MediaId` wrapper VO (UUID-format protovalidate; UUIDv7 is a server-minting convention, not a proto rule). Variant URLs are server-composed at read time, NOT persisted (design D6)
- [x] 1.2 `entity/v1/series.proto` (**BREAKING**): rename field 7 `cover_image` → `media`, retype `Url` → `entity.v1.Media`, `reserved "cover_image"` for the old name
- [x] 1.3 `rpc/organizer/v1/concert_service.proto` (**BREAKING**): remove the shipped `UploadCoverImage`; add `CreateMediaUploadURL` (req: content_type → resp: upload_url `Url`, media_id `MediaId`, max_bytes) + `AttachMedia` (req: series_id, media_id → empty resp: the image is not yet live, so nothing meaningful to return) with protovalidate + error docs; keep other verbs
- [x] 1.4 `MEDIA.uploaded` event payload contract (`{ media_id, series_id }` — `series_id` lets the consumer own the `series_media` cut-over, see 4.5) documented alongside existing event data
- [x] 1.5 `buf lint`/`format`/`breaking` (add `buf skip breaking` label for the intentional break); spec PR merge → Release → BSR gen

## 2. Cloud-provisioning

- [x] 2.1 New `organizer-media-internal` bucket (PRIVATE, no LB/CDN, uniform bucket-level access) for uploaded originals at `{org}/{mediaId}`: CORS allow `PUT` from the organizer Web App origin (dev localhost:9100 + `organizer.dev.…`; prod `organizer.…`), response headers `Content-Type`, `x-goog-content-length-range`. The served `organizer-media` bucket is unchanged (keeps `cdn/` prefix + LB). Two-bucket split (not an `internal/` prefix) so the served bucket's URL map never exposes originals — see design D5
- [x] 2.2 media-processor image: Artifact Registry repo/entry for the new consumer image (backend `cmd/job`), prod immutable-tag policy consistent with existing repos
- [x] 2.3 Workload Identity: `media-processor` GSA + WI binding — bucket-scoped `objectAdmin` on **both** buckets: read/delete on `organizer-media-internal` (originals) + write on `organizer-media` (`cdn/` variants); no project-level storage role
- [x] 2.4 KEDA `ScaledJob` (`scaledobject.yaml`) triggered on JetStream `MEDIA.uploaded` (durable `media_uploaded`): resource requests/limits sized for libvips, `maxReplicaCount`, `backoffLimit`, spot nodeSelector (dev), `restartPolicy: Never`
- [x] 2.5 `kubectl kustomize` dry-run for the new Job overlay(s) (dev + prod) — resources set, spot nodeSelector, no empty `resources: {}`
- [x] 2.6 media-consumer DB access (surfaced post-cut-over; design D10): the consumer owns the `series_media` cut-over (`FindMediaByID` + transactional upsert), so it needs Cloud SQL — a `media-consumer@<project>.iam` IAM DB user (Pulumi `gcp.sql.User`), `roles/cloudsql.client` + `roles/cloudsql.instanceUser` on the media-consumer GSA, the `DATABASE_*` ConfigMap block (PSC-direct, in-process connector, IAM auth), and an app-schema grant migration — with `pulumi up` (creates the user) ordered **before** the grant migration. Shipped as a follow-up (cloud-provisioning#470 + backend#424)

## 3. Backend — API (upload/attach)

- [x] 3.1 GCS storer: add `SignedPutURL(bucket, key, contentType, maxBytes, ttl)` (V4, keyless via IAM SignBlob; `x-goog-content-length-range` condition) and **restore** a prefix-delete (`DeletePrefix`) for reclaim
- [x] 3.2 `CreateMediaUploadURL` usecase + handler: **org-scoped auth** (caller is an organizer; no series is referenced yet), validate content type (JPEG/PNG/WebP), mint `mediaId` (UUIDv7), return signed `PUT` URL for `internal/{org}/{mediaId}` (15-min TTL) + `mediaId` + `max_bytes` (the single-source byte limit the client echoes as `x-goog-content-length-range`; matches the signed-URL condition)
- [x] 3.3 `AttachMedia(series_id, media_id)` usecase + handler: **verify the caller OWNS `series_id`** (represented-artist ownership, not merely org-scoped — deny non-owners without revealing existence), INSERT the `media` row (idempotent per `media_id`), publish `MEDIA.uploaded { media_id, series_id }`, return empty. Do NOT re-point `series_media` here and do NOT delete the previous image's prefix — the **consumer owns the `series_media` cut-over** and reclaims the old prefix after writing the new variants (see 4.5), so an already-published concert keeps serving its old image with no 404 window
- [x] 3.4 Remove the shipped `UploadCoverImage` handler/usecase/mapper path; mapper returns `Media { kind, attributes }` where `attributes.thumb`/`attributes.large` are composed per exposure from `{ORGANIZER_MEDIA_CDN_BASE}/cdn/{org}/{mediaId}/{variant}.webp` (via the media/series_media join)
- [x] 3.5 `MEDIA` stream in `streams.go` (+ KEDA trigger already in 2.4); DI wiring
- [x] 3.6 Unit tests: signed-URL issuance (type/size constraints), `AttachMedia` series-ownership reject (non-owner denied), attach idempotency, mapper variant URLs; `make check` with upgraded BSR

## 4. Backend — media-processor consumer (`cmd/job`)

- [x] 4.1 Introduce libvips (govips) dependency; `cmd/job` build target + Dockerfile for the media-processor image
- [x] 4.2 `MediaConsumer` (behavior `media_uploaded`): pull message → load `media` row → read `internal/{org}/{mediaId}`
- [x] 4.3 Safety: magic-byte validation + header-first pixel/edge limit (≈50 MP / 8000 px) rejected **before** full decode; reject SVG/other
- [x] 4.4 Processing: strip EXIF, encode WebP `thumb` (~800w) + `large` (~1920w), aspect preserved (no crop), immutable `Cache-Control`; write `cdn/{org}/{mediaId}/{variant}.webp`
- [x] 4.5 On success: write new variants → **cut over in one transaction**: upsert `series_media(series_id)` → the new `media_id`, capturing the old `media_id` first if a row existed → **then** reclaim the previous image's `cdn/{org}/{old}/` prefix + delete the old `media` row (deferred until here so an already-published concert keeps serving its old variants until the replacement is ready) → delete the `internal/` original → ack. Transient failure = nak (`max_deliver=3`). Permanent failure (invalid image) = `term` + **delete the `internal/` original** (so failed uploads do not linger) + log/metric (reuse poison-consumer pattern). Idempotent on redelivery: deterministic variant overwrite, cut-over upsert is a no-op if already done, old-prefix/original deletes are no-ops if already gone
- [x] 4.6 Unit/integration tests: valid image → variants + EXIF removed; oversized-dimension rejected pre-decode; invalid bytes → no variants + term + original deleted; replace = new variants written **and** `series_media` cut over to the new media **before** the old prefix/row are reclaimed (no 404 window); first upload = `series_media` inserted by the consumer; idempotent reprocess

## 5. Frontend (organizer console) — REMAINING WORK

The organizer console authoring app **now exists** (#573, organizer-event-authoring)
and shipped the cover-image UI against the **synchronous** `uploadCoverImage(bytes)`
RPC. This change removed that RPC on the backend (§1.3, §3.4) **without** migrating
the console, so the console's cover-upload currently calls a removed RPC and is
broken. This section migrates it to the async pipeline. This is the change's
remaining active work.

- [x] 5.1 Upgrade the frontend BSR schema to the release that removed `UploadCoverImage` and added `CreateMediaUploadURL` + `AttachMedia` + `Series.media: Media` (current pin predates it); pin the 1.x protobuf-es build per the consumer-upgrade gotchas
- [x] 5.2 Replace `concert-editor` cover upload: `CreateMediaUploadURL` → direct `PUT` to GCS (Content-Type + `x-goog-content-length-range` headers) → `AttachMedia`; keep the existing client-side type/size pre-check (`cover-image.ts`), retype `readFileBytes`-based flow to the signed-URL flow
- [x] 5.3 Optimistic **local blob** preview during/after upload; render `Series.media` as `Media` variants (thumb/large), 404-graceful until processed, with a re-upload path when an image never appears
- [x] 5.4 `make check` with the upgraded BSR (biome + tsc + tests)

## 6. Observability

- [x] 6.1 Alerting: added a `media-processor` ERROR-log AlertPolicy (system failures page; invalid uploads log WARN, not ERROR); queue backlog for the `media_uploaded` durable is already covered by the existing unfiltered `Consumer JetStream Backlog Stall` policy (`nats_consumer_num_pending`). Bespoke processing-latency/success-count **metric emission is deferred** (thresholds tune post-launch; the ERROR-log + backlog signals cover the incident classes at MVP)

## 7. Release & ship to prod

- [x] 7.1 Backend PR merged → release → prod pin bump (API + media image). Shipped v1.49.0 (pipeline) then v1.50.0 (declarative-jetstream-nack rework: media-consumer image) + the DB grant migration (backend#424).
- [x] 7.2 Cloud-provisioning PR merged → prod `pulumi up` (Console) — CORS, originals bucket, media-consumer WI SA + IAM DB user + cloudsql roles, KEDA `ScaledObject` on the NACK-owned durable. (dev auto-`pulumi up` is moot — dev decommissioned.)
- [ ] 7.3 Frontend release: migrate the organizer console cover-upload (§5) to the async pipeline, upgrade BSR, ship (organizer-console-web). Coordinate the prod-pin bump.
- [ ] 7.4 Verify in prod: organizer uploads an image for an owned draft **via the console** → processed WebP `thumb`/`large` served over `https://media.…/cdn/{org}/{mediaId}/…` (EXIF removed); replace reclaims old variants; a malformed/oversized-dimension image yields no variants; publish is independent of processing. *(Backend/infra path — wake-from-zero, bind, DB connect, ack — already prod-verified with a synthetic event; §7.4 confirms the full real-upload path once §5 ships.)*
