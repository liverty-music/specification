## Why

Vetted organizers can now sign in to the organizer console (roadmap step ①
is complete: tenancy, accounts, console, rpc-server all shipped), but they
have **no way to publish their own concerts** — the only path into the
concert data model is the discovery / auto-publish pipeline. This change
(roadmap step ②) gives an organizer a **minimal first-party authoring
path**: create and publish a concert for an artist they represent, as an
**informational event page**, which supersedes scraped data and takes that
artist out of the scraping pipeline. Ticketing (price, lottery, purchase)
is out of scope — this delivers the M1 milestone (organizers publish →
followers get notified) together with ③. **Builds on
`fix-series-fragmentation` (spec#869)** (series-grouped discovery +
publish-once-per-series + shared series-resolution helper) and sequences
after its backend implementation. Tracked by liverty-music/specification#759.
Extensions are deferred to `organizer-event-authoring-extensions`.

## What Changes

- **Minimal authoring data model.** Extend the existing `Series` aggregate
  with the smallest set of authoring fields: `description` (plain body
  text), `cover_image` (one image), `visibility` (`PUBLIC` / `UNLISTED`),
  `publish_state` (`DRAFT` / `PUBLISHED` / `CANCELLED`), and `organizer_id`
  (the owning organizer). Times stay at the **`Event` (performance) level**
  (a 2部制 day = multiple `Event`s under one `Series`); reuse `Event`,
  `Venue` (geocoded), and `event_performers` unchanged.
- **Dedicated `rpc.organizer.v1.ConcertService`** (org-scoped, bare-verb,
  mirroring admin `ConcertService`; the identity `OrganizerService` stays
  `Get`/`ListArtists`): `Create`, `Update` (draft or published correction),
  `Cancel`, `Publish`, `UploadCoverImage`, `RegenerateToken`, `List` (own).
  Fields are wrapper VOs (`Url` for cover image, `Description` VO); enum
  final shapes declared now (`Visibility` reserves `PASSWORD`; `PublishState`
  reserves `SCHEDULED`) so extensions is additive.
- **Org-scoped authorship.** An organizer may author only for artists it
  represents (reuse `ListArtists` / the org-scoped role claim). Venue is
  resolved via the existing Places get-or-create helper.
- **Publish + notification gating (series-grouped, per #869).**
  `CONCERT.created` drives the existing follower push, so a `PUBLIC` publish
  emits **one `CONCERT.created` per series** (the publish-once model from
  `fix-series-fragmentation`), carrying the published events' ids; `DRAFT` /
  `UNLISTED` never emit.
- **Supersede via the shared series-resolution + natural-key upsert** (not
  the removed AdoptStaged path): a matching pending `staged_concert` is
  dropped; an already-published discovered event is **claimed** (re-pointed
  to the organizer's series, id kept, marked organizer-owned, no re-notify);
  a **suppressed** slot is not silently resurrected; a slot owned by a
  **different organizer** is a conflict routed to admin, not a takeover.
- **Scraping exclusion filters the discovery cron** (skip
  `SearchNewConcerts` for associated artists — before the Gemini call), keyed
  on the Organizer↔Artist association: associating stops scraping,
  disassociating or deactivating resumes it.
- **Visibility.** `PUBLIC` events appear in normal discovery; `UNLISTED`
  events are reachable only via a **signed tokenized URL** (not referrer
  control) and are excluded from discovery/lists.
- **Cover-image hosting.** Organizer-uploaded image → object storage →
  served (the one genuinely new piece of infrastructure).
- **Organizer console screens.** List own concerts; create / edit / cancel /
  publish an event, with cover-image upload.

## Capabilities

### New Capabilities
- `organizer-event-authoring`: an organizer authors and publishes a
  first-party concert (draft → publish), scoped to its represented artists,
  with public/unlisted visibility, cover image, and the publish-time
  supersede + scraping-exclusion behavior.

### Modified Capabilities
- `event-management`: the `Series` aggregate gains authoring fields
  (`description`, `cover_image`, `visibility`, `publish_state`,
  `organizer_id`) and a draft/published/cancelled lifecycle.
- `auto-concert-discovery`: the scheduled job SHALL skip artists associated
  with an active organizer (exclusion filters the artist list before
  `SearchNewConcerts`).

## Impact

- **specification**: additive fields on `entity/v1/series.proto`
  (description, cover_image, visibility enum, publish_state enum,
  organizer_id); new authoring RPCs + messages on
  `rpc/organizer/v1/organizer_service.proto`. Non-breaking; ships via the
  cross-repo release order.
- **backend**: Series authoring fields + migration; organizer authoring
  usecase (reusing `resolveOrCreateVenue` / `buildAndInsertConcerts`);
  Publish → `CONCERT.created` + supersede + discovery-exclusion hook;
  unlisted-URL token sign/verify; cover-image upload + object storage.
- **frontend**: organizer console authoring screens (create/edit/publish +
  image upload); unlisted-event route that validates the token.
- **cloud-provisioning**: an object-storage bucket for organizer cover
  images (+ serving/CDN); org-scoped access.
- **Non-goals (deferred):** ticket types / price / capacity / sale method /
  lottery (④ `lottery-application`); and all richer authoring —
  `organizer-event-authoring-extensions` (multiple images, YouTube embed,
  streaming mode, category/keywords, structured 注意事項 / 問い合わせ先 /
  年齢制限, password-protected visibility, per-event description, performer
  order/roles, co-organizer).
