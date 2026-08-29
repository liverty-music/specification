## Why

The shipped organizer media path (② `organizer-event-authoring`) has the
API server receive the raw bytes and write a single unprocessed object to
`cdn/{org}/{media_id}`. That ties image handling to app compute, ships raw files
(EXIF metadata intact, no next-gen format, one size for every surface), and does
not scale. This change replaces it with a proper async media pipeline —
direct-to-GCS upload, off-API image processing, and responsive CDN delivery —
before the authoring UI goes live in prod, so users never see the raw path.

## What Changes

- **BREAKING** Replace `ConcertService.UploadMedia` (backend receives
  bytes) with two RPCs: `CreateMediaUploadURL` (returns a short-lived GCS **V4
  signed PUT URL** + a minted `MediaId`) and `AttachMedia` (records the media
  and enqueues processing). The Web App uploads the original **directly to GCS**.
- **BREAKING** `entity.v1.Series.media` changes from a single `Url` to an
  `entity.v1.Media` message carrying responsive variant URLs (`thumb`, `large`).
- **Async processing** off the API: a behavior-named JetStream consumer
  (`MEDIA.uploaded`, durable `media_uploaded`) run as a KEDA `ScaledJob`
  (scale-to-zero) validates magic bytes, enforces pixel/dimension limits
  (decompression-bomb defense), strips EXIF, and encodes **WebP** responsive
  variants into `cdn/{org}/{media_id}/{variant}.webp`.
- **Single bucket, two prefixes**: reuse the existing `organizer-media` bucket —
  add a private `internal/` prefix (CORS `PUT` target, not CDN-routed) for the
  uploaded original; keep `cdn/` for served variants.
- **Cleanup**: the processor deletes the original on success; replacing an image
  deletes the previous media's `cdn/{org}/{old}/` prefix (restore a
  prefix-delete on the storer).
- No processing **status** is stored: readiness is the served object's
  existence; the console shows an optimistic local preview and a re-upload path
  on failure.

## Capabilities

### New Capabilities
<!-- None. The media pipeline refines the existing media requirement rather
     than introducing a separate user-facing capability. -->

### Modified Capabilities
- `organizer-event-authoring`: the media requirement changes from a
  synchronous single-object upload to a direct-upload + async-processing +
  responsive-variant pipeline (signed PUT URL, WebP variants, EXIF strip,
  pixel-limit safety, object-existence readiness, replace/cleanup semantics),
  and `Series.media` becomes an `entity.v1.Media`.

## Impact

- **specification (proto)**: `entity/v1/media.proto` (new `Media`, `MediaId`);
  `entity/v1/series.proto` (`media`: `Url` → `Media`); new
  `MEDIA.uploaded` event; `rpc/organizer/v1/concert_service.proto` — remove
  `UploadMedia`, add `CreateMediaUploadURL` + `AttachMedia`. New BSR release.
- **backend**: new upload/attach usecase + handlers; `SignedPutURL` on the GCS
  storer + restore prefix-delete; new `MediaConsumer` (govips/libvips image
  processing) wired in the consumer/`cmd/job` deployable; `MEDIA` stream in
  `streams.go`; remove the old `UploadMedia` path; mapper returns `Media`.
- **cloud-provisioning**: `organizer-media` bucket CORS (`PUT` from the organizer
  Web App origin) + the `internal/` prefix convention; new `media-processor`
  image (Artifact Registry) + Workload Identity SA (read/delete `internal/`,
  write `cdn/`); KEDA `ScaledJob` trigger on `MEDIA.uploaded`.
- **frontend**: image upload reworked to `CreateMediaUploadURL` → direct `PUT` →
  `AttachMedia`, optimistic local preview, `thumb`/`large` variant rendering.
- **Non-Goals**: content moderation (NSFW/abuse detection); multiple images /
  gallery, video, and YouTube embeds (deferred to
  `organizer-event-authoring-extensions`, which reuses this pipeline);
  password-protected visibility.
