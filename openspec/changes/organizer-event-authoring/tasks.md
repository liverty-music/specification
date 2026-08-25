## 1. Specification (proto)

- [x] 1.1 `entity/v1/series.proto` (additive, wrapper VOs per convention): `description` (`Description` VO, protovalidate length), `cover_image` (`Url` VO), `Visibility` enum (`UNSPECIFIED`/`PUBLIC`/`UNLISTED`; reserve `PASSWORD`), `PublishState` enum (`UNSPECIFIED`/`DRAFT`/`PUBLISHED`/`CANCELLED`; reserve `SCHEDULED`), `organizer_id`; unlisted token backend-only (not on read DTO)
- [x] 1.2 New `rpc/organizer/v1/concert_service.proto` — `ConcertService` (bare verbs) `Create`, `Update`, `Cancel`, `Publish`, `UploadCoverImage`, `RegenerateToken`, `List` + messages + error docs; keep identity `OrganizerService` unchanged
- [ ] 1.3 `buf lint`/`format`/`breaking` (✅ pass locally); spec PR merge → Release → BSR gen (pending)

## 2. Cloud-provisioning

- [ ] 2.1 GCS bucket for organizer cover images + serving/access (Pulumi)

## 3. Backend

- [ ] 3.1 Atlas migration: `series` columns (description, cover_image_url, visibility, publish_state, organizer_id FK, unlisted_token, domain-specific `*_at`); index for state/visibility filtering
- [ ] 3.2 Authoring usecase: create draft (Series+Event(s)+performers) reusing the **fix-series-fragmentation shared series-resolution helper** + `resolveOrCreateVenue` + natural-key event upsert (NOT the removed AdoptStaged path); ownership check vs represented artists; validation (title/date required, open≤start, future date)
- [ ] 3.3 List own concerts (drafts + published); edit draft; edit published (correction, no re-notify); `Cancel` (mark CANCELLED — terminal, drop from fan surfaces, **emit `CONCERT.cancelled`** for consumers/caches)
- [ ] 3.4 `Publish`: emit **one `CONCERT.created` per series** (carrying the published events' ids) for PUBLIC only; DRAFT/UNLISTED never emit; publishing a new event under an already-published series emits once for the new event id(s)
- [ ] 3.5 Supersede in publish txn: drop matching `staged_concert`; **claim** an already-published discovered event (re-point to organizer's series, keep id, mark organizer-owned, no re-emit); **do not resurrect a suppressed slot** without explicit action; route a **different-organizer** slot to admin reconciliation (no auto takeover)
- [ ] 3.6 Discovery exclusion in the cron: filter `FollowRepo.ListAll` by Organizer↔Artist association **before** `SearchNewConcerts` (skip the Gemini call); resumes on disassociate/deactivate
- [ ] 3.7 Unlisted token: HMAC sign on publish + verify on public read path + `RegenerateToken`; shared guard excludes DRAFT/UNLISTED/CANCELLED from all list/discovery/follower/notify queries
- [ ] 3.8 Cover-image upload → GCS with server-side type/size validation
- [ ] 3.9 Emit `organizer.concert.published` analytics event
- [ ] 3.10 `ConcertService` authoring handlers behind org-scoped authorization
- [ ] 3.11 Unit tests: ownership reject, notify-once/never (draft+unlisted), merge-supersede no double-notify, association exclusion on/off, draft/unlisted/cancelled never leak, token verify+regenerate, cancel; `make check` with upgraded BSR

## 4. Frontend (organizer console)

- [ ] 4.1 Authoring screens: create/edit draft (title, description, date, open/start, venue, performers from `ListArtists`), cover upload, visibility, Publish; list own concerts; edit-published + Cancel
- [ ] 4.2 Unlisted-event public route that validates the tokenized URL
- [ ] 4.3 `make check` with upgraded BSR

## 5. Release & ship to prod

- [ ] 5.1 Backend PR merged → release → prod pin bump (after IaC bucket applied)
- [ ] 5.2 Frontend PR merged → release
- [ ] 5.3 Cloud-provisioning PR merged → ArgoCD synced (bucket)
- [ ] 5.4 Verify in prod: organizer creates draft for a represented artist, uploads cover, publishes PUBLIC → `CONCERT.created` once → follower notified; a matching scraped/discovered record is superseded (merge, no double-notify); associating an artist stops its scraping and disassociating resumes it; UNLISTED reachable only by token (regenerate invalidates old); edit/cancel behave per spec
