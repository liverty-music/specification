## Context

See proposal.md — Why. ② `organizer-event-authoring` shipped a synchronous
media path (API receives bytes → writes one object to `cdn/{org}/{media_id}` in
the private `organizer-media` bucket, served via Cloud CDN behind an external
ALB; `series_media` join + generic `media` table already exist). The stack uses
NATS JetStream + KEDA for async work, Workload Identity for GCS access, and
Cloudflare **DNS-only** in front of a GKE Gateway ALB. This design reworks the
media path into an async pipeline **before** the authoring UI (#573) is released
to prod, so no raw-path images ever ship.

## Goals / Non-Goals

**Goals:** direct-to-GCS upload (no bytes through the API), off-API image
processing (EXIF strip, WebP, responsive variants), decompression-bomb safety,
CDN delivery, and least-privilege cleanup — for a **single image per series**,
built on the generic `media`/`series_media` model so it generalizes to N images.

**Non-Goals (design-level):** multiple images / gallery, video, YouTube embeds
(deferred to `organizer-event-authoring-extensions`, which reuses this
pipeline); content moderation; a stored processing-status model; art-directed
cropping; JPEG/AVIF fallbacks.

## Decisions

**D1 — Scope: media *infrastructure* for one image, generalizes to N. [★A]**
This change is the ingest→process→serve plumbing for a single image. Gallery /
video / links stay in extensions and reuse the same `media` rows, consumer, and
buckets. Keeps media behavior cohesive and independently shippable.

**D2 — Process on upload, not on publish. [★B]**
The consumer runs when the original is uploaded (during draft), so the console
gets an immediate preview and `Publish` is decoupled from processing. Draft
variants therefore live under `cdn/` (obscurity-protected by the unguessable
`media_id`) — consistent with the shipped MVP decision that drafts sit under
`cdn/`. *Alternative (process on publish)* gives hard draft isolation but
reintroduces signed-URL draft preview and couples publish to processing;
rejected for MVP.

**D3 — No stored processing status; readiness = object existence. [★C]**
No `status` column (the shipped `media(id, organizer_id, kind, attributes)`
stays). The read DTO always derives the variant URLs; the console shows an
optimistic **local blob preview** during active upload and is **404-graceful**
on revisit; a failed image simply never appears → the organizer re-uploads.
Because processing is on upload (D2), the published page effectively never hits
the processing window. *Alternative (PROCESSING/READY/FAILED column + polling)*
adds schema, DTO, and client machinery for a distinction MVP does not need;
deferred until failures are common or active failure notification is required.

**D4 — Async via a behavior-named JetStream consumer on a KEDA ScaledJob. [★D]**
`AttachMedia` publishes `MEDIA.uploaded { media_id, series_id }` (snake_case wire
contract). The object keys are derived from the media id + the row's
`organizer_id` (looked up from the `media` row), so `media_id` alone would locate
the original and the variant prefix; `series_id` is carried **because the
consumer owns the `series_media` cut-over** (D7) — on a replace it must find the
series' currently-attached (old) media, which is no longer reachable from the new
`media_id` once processing begins. A
durable pull consumer `media_uploaded` (behavior-named per repo convention) is
run as a **KEDA `ScaledJob`** in the `cmd/job` deployable — isolating libvips
(CGO) from the API and the always-on consumer, and scaling to zero for rare
bursty work. Ack on success; nak with `max_deliver = 3` on transient failure;
`term` + log on permanent failure (invalid image). **No DLQ stream** — final
failures emit a log + metric + alert (reuse the existing poison-consumer
pattern). Idempotent: variant keys are deterministic from `(org, mediaId)`, so
redelivery overwrites harmlessly; `AttachMedia` is a no-op for an already-attached
`mediaId`. The `MEDIA` stream (`streams.go`) and the KEDA trigger
(`scaledobject.yaml`) MUST land in the same change (a new subject without its
stream/trigger crashloops in prod).

**D5 — Single bucket, `internal/` + `cdn/` prefixes; 2 variants, aspect-preserved. [★E]**
Reuse the deployed `organizer-media` bucket:
`internal/{org}/{mediaId}` (private, not CDN-routed, CORS `PUT` target for the
signed upload) and `cdn/{org}/{mediaId}/{variant}.webp` (CDN-served). Two
width-bounded variants — `thumb` (~800w) and `large` (~1920w) — **aspect
preserved, no crop** (concert posters are portrait/square/landscape; the
frontend crops visually via `object-fit`). *Alternative (separate staging
bucket)* adds infra for no MVP benefit; rejected.

**D6 — `entity.v1.Media` mirrors the DB's open polymorphism (`kind` + `attributes`); variant URLs are server-composed, not stored. [★E/naming]**
The exposed media entity mirrors the shipped `media(id, organizer_id, kind,
attributes)` row rather than being a role-named type:
`Media { MediaId id; MediaKind kind; MediaAttributes attributes }`.
- `MediaKind` is a proto enum **1:1 with the PG `media_kind` ENUM** (`IMAGE` only
  at MVP). A new kind is additive on both sides — `ALTER TYPE media_kind ADD
  VALUE` + an appended enum value.
- `MediaAttributes` is a flat, **all-optional read projection** of the row (NOT a
  literal copy of the JSONB column): for `IMAGE` it carries `Url thumb` (~800w)
  and `Url large` (~1920w); extensions append `poster`/`stream`/`duration`
  (VIDEO) and `youtube_video_id` (YOUTUBE) as further optional fields — purely
  additive, no structural change. The open bag's type-safety is recovered with a
  **kind-gated protovalidate CEL** (e.g. `kind == IMAGE ⇒ thumb, large set`).
- *Rejected: a closed `oneof`* — type-safe but it fights the DB's deliberately
  open enum+JSONB model (every `media_kind` value would also have to be added to
  the oneof), creating a second source of polymorphism truth.

The variant URLs are **derived, not persisted**: the DB stores no URL
(`cover_image_url` was dropped); the read mapper composes
`{ORGANIZER_MEDIA_CDN_BASE}/cdn/{org}/{mediaId}/{variant}.webp` at read time and
exposes it as a field. They are *derivable* but MUST NOT be reduced to an
id-only response — the CDN base, key layout, variant names, and extension stay
server-side so the client never hardcodes the storage convention (env-specific
base and future variants stay additive server-side). No existence check on
compose: the client is 404-graceful until processing finishes (D3).

`Series.media` is a single `Media` (field 7, **renamed from `cover_image`**,
retyped `Url` → `Media`); extensions generalizes it to `repeated Media`.

**D7 — Consumer owns the cut-over and cleanup; no lifecycle. [★F]**
`AttachMedia` does **not** re-point `series_media`: it inserts the new `media`
row and publishes `MEDIA.uploaded { media_id, series_id }`, leaving the series
pointing at whatever it pointed at before (the old media on a replace, nothing on
a first upload). The **consumer** performs the atomic cut-over after it has
written the new variants: in one transaction it upserts `series_media(series_id)`
→ the new `media_id`, and — if an old row existed — captures the old `media_id`
first. This makes the consumer the single owner of the "an image becomes live"
transition, which is exactly what keeps the no-404 invariant true (D3): the old
variants stay served until the new ones exist. Only **after** the cut-over does
the consumer delete the *previous* media's `cdn/{org}/{old}/` prefix (and the old
`media` row). It also deletes the `internal/{org}/{mediaId}` original once it is
done with it — on **both** success **and** permanent failure (`term`) — so a
failed upload does not linger. Everything is idempotent on redelivery: the
variant keys are deterministic, the upsert is a no-op if already cut over, and
the prefix/original deletes are no-ops if already gone. Restore a prefix-delete
on the storer (removed in the media rework). No bucket lifecycle rule: only
truly abandoned uploads (a signed `PUT` that is never followed by `AttachMedia`,
so the consumer never sees it) can orphan, and those are rare and tiny — add a
rule later if needed. `Cancel` does not touch GCS (the shared visibility guard
already excludes cancelled from
fan surfaces).

**D8 — Two-layer input safety. [★H]**
The frontend pre-checks dimensions before upload (UX only — a client can bypass
it and `PUT` directly via the signed URL). The **consumer is the security
boundary**: it reads dimensions from the header **before** full decode and
rejects images over a pixel/edge limit (≈50 MP / 8000 px) — cheap, no bomb
allocation. Accept only JPEG/PNG/WebP (signed-URL content type **and**
magic-byte re-check); SVG excluded (XSS). Moderation is a non-goal.

**D9 — Replace the shipped `UploadCoverImage`; no data migration; pipeline-first. [★K/★M]**
Remove the shipped `ConcertService.UploadCoverImage` (bytes-through-the-API);
add `CreateMediaUploadURL` (mints `mediaId`, returns a
V4 signed `PUT` URL for `internal/{org}/{mediaId}`) + `AttachMedia(seriesId,
mediaId)`. The series field `cover_image` (`Url`, field 7) is **renamed to
`media` and retyped to `Media`** in the same break (D6). No prod media data
exists (frontend not released), so **no data
migration**. Ship the pipeline **before** the authoring media UI goes live so
users never see the raw path. Output is **WebP only** (Baseline); no JPEG/AVIF
fallback; original not retained (D7). Signing is keyless via IAM SignBlob (WI
SA), so DRS is not involved (own-SA, own-domain).

## Risks / Trade-offs

- **Draft variants are obscurity-protected, not hard-isolated** (D2) → accepted
  for low-sensitivity image (consistent with the shipped decision); the
  unguessable `media_id` never appears until the organizer renders it.
- **Poison image loops** (D4) → `max_deliver = 3` + `term` on permanent failure;
  log/metric/alert instead of a DLQ.
- **Decompression bomb** (D8) → header-first dimension check before decode; the
  ScaledJob also has a memory limit as a backstop.
- **Client bypass of frontend validation** (D8) → the consumer, not the client,
  is the enforcing boundary.
- **New deployable (media-processor image)** → adds an Artifact Registry image +
  WI SA + KEDA wiring; contained to this change, isolates libvips from the API.
- **Orphan variants on replace** (D7) → prefix-delete restored on the storer;
  abandoned-upload orphans accepted (rare/tiny).

## Migration Plan

1. spec: `entity/v1/media.proto` + `Series.media: Media` (field 7 renamed from
   `cover_image`) + `MEDIA.uploaded { media_id, series_id }`
   + `concert_service` (remove `UploadCoverImage`, add `CreateMediaUploadURL` +
   `AttachMedia`) → Release → BSR gen.
2. cloud-provisioning: `organizer-media` CORS (`PUT` from organizer Web origin);
   media-processor image repo (Artifact Registry) + WI SA (read/delete
   `internal/`, write `cdn/`); KEDA `ScaledJob` trigger on `MEDIA.uploaded`.
3. backend: `SignedPutURL` + restore prefix-delete on the GCS storer; upload/
   attach usecase + handlers; `MediaConsumer` (govips: magic-byte, header pixel
   limit, EXIF strip, WebP thumb/large, write `cdn/`, delete original);
   `MEDIA` stream in `streams.go`; remove `UploadCoverImage`; mapper → `Media`.
4. frontend: image upload → `CreateMediaUploadURL` → direct `PUT` → `AttachMedia`,
   optimistic local preview, `thumb`/`large` rendering.
5. release → prod verify (upload → processed WebP variants served via CDN;
   replace reclaims old; bad image yields no variants).
- Rollback: additive infra; the new RPCs replace the old one atomically at the
  BSR release; no media data to preserve.

## Open Questions

- Exact variant widths and the pixel/edge limit — tunable in implementation
  without changing specs or tasks.
- `media-processor` resource requests/limits + KEDA `maxReplicaCount` — set from
  libvips memory during implementation.
- Processing metrics/alerts (latency, failure rate, queue depth) — observability
  wiring, enumerated in tasks; thresholds tuned post-launch.
