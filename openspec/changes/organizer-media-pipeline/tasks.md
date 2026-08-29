## 1. Specification (proto)

- [ ] 1.1 `entity/v1/media.proto`: new `Media` (`MediaId id`, `Url thumb`, `Url large`; reserve fields for future `kind`/`attributes`) + `MediaId` wrapper VO (UUIDv7 protovalidate)
- [ ] 1.2 `entity/v1/series.proto` (**BREAKING**): `media` type `Url` → `entity.v1.Media`
- [ ] 1.3 `rpc/organizer/v1/concert_service.proto` (**BREAKING**): remove `UploadMedia`; add `CreateMediaUploadURL` (req: content_type → resp: upload_url `Url`, media_id `MediaId`) + `AttachMedia` (req: series_id, media_id) with protovalidate + error docs; keep other verbs
- [ ] 1.4 `MEDIA.uploaded` event payload contract (`{ media_id }`) documented alongside existing event data
- [ ] 1.5 `buf lint`/`format`/`breaking` (add `buf skip breaking` label for the intentional break); spec PR merge → Release → BSR gen

## 2. Cloud-provisioning

- [ ] 2.1 `organizer-media` bucket: CORS allow `PUT` from the organizer Web App origin (dev localhost + prod), response headers `Content-Type`, `x-goog-content-length-range`; document the `internal/` (private, PUT target) vs `cdn/` (served) prefix convention
- [ ] 2.2 media-processor image: Artifact Registry repo/entry for the new consumer image (backend `cmd/job`), prod immutable-tag policy consistent with existing repos
- [ ] 2.3 Workload Identity: `media-processor` GSA + WI binding — bucket-scoped `objectAdmin` on `organizer-media` (read/delete `internal/`, write `cdn/`); no project-level storage role
- [ ] 2.4 KEDA `ScaledJob` (`scaledobject.yaml`) triggered on JetStream `MEDIA.uploaded` (durable `media_uploaded`): resource requests/limits sized for libvips, `maxReplicaCount`, `backoffLimit`, spot nodeSelector (dev), `restartPolicy: Never`
- [ ] 2.5 `kubectl kustomize` dry-run for the new Job overlay(s) (dev + prod) — resources set, spot nodeSelector, no empty `resources: {}`

## 3. Backend — API (upload/attach)

- [ ] 3.1 GCS storer: add `SignedPutURL(bucket, key, contentType, maxBytes, ttl)` (V4, keyless via IAM SignBlob; `x-goog-content-length-range` condition) and **restore** a prefix-delete (`DeletePrefix`) for reclaim
- [ ] 3.2 `CreateMediaUploadURL` usecase + handler: validate content type (JPEG/PNG/WebP), ownership vs represented artists, mint `mediaId` (UUIDv7), return signed `PUT` URL for `internal/{org}/{mediaId}` (15-min TTL) + `mediaId`
- [ ] 3.3 `AttachMedia` usecase + handler: create/replace the `media` + `series_media` rows (idempotent per `mediaId`), reclaim the previous image's `cdn/{org}/{old}/` prefix, publish `MEDIA.uploaded { mediaId }`; org-scoped auth
- [ ] 3.4 Remove `UploadMedia` handler/usecase/mapper path; mapper returns `Media { thumb, large }` (URLs derived per exposure from the media/series_media join)
- [ ] 3.5 `MEDIA` stream in `streams.go` (+ KEDA trigger already in 2.4); DI wiring
- [ ] 3.6 Unit tests: signed-URL issuance (type/size constraints), ownership reject, attach idempotency + replace-reclaim, mapper variant URLs; `make check` with upgraded BSR

## 4. Backend — media-processor consumer (`cmd/job`)

- [ ] 4.1 Introduce libvips (govips) dependency; `cmd/job` build target + Dockerfile for the media-processor image
- [ ] 4.2 `MediaConsumer` (behavior `media_uploaded`): pull message → load `media` row → read `internal/{org}/{mediaId}`
- [ ] 4.3 Safety: magic-byte validation + header-first pixel/edge limit (≈50 MP / 8000 px) rejected **before** full decode; reject SVG/other
- [ ] 4.4 Processing: strip EXIF, encode WebP `thumb` (~800w) + `large` (~1920w), aspect preserved (no crop), immutable `Cache-Control`; write `cdn/{org}/{mediaId}/{variant}.webp`
- [ ] 4.5 Success = delete `internal/` original + ack; transient failure = nak (`max_deliver=3`); permanent failure (invalid image) = `term` + log/metric (reuse poison-consumer pattern); idempotent overwrite on redelivery
- [ ] 4.6 Unit/integration tests: valid image → variants + EXIF removed; oversized-dimension rejected pre-decode; invalid bytes → no variants + term; idempotent reprocess

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
