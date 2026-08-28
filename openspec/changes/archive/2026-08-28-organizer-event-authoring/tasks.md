## 1. Specification (proto)

- [x] 1.1 `entity/v1/series.proto` (additive, wrapper VOs per convention): `description` (`Description` VO, protovalidate length), `cover_image` (`Url` VO), `Visibility` enum (`UNSPECIFIED`/`PUBLIC`/`UNLISTED`; reserve `PASSWORD`), `PublishState` enum (`UNSPECIFIED`/`DRAFT`/`PUBLISHED`/`CANCELLED`; reserve `SCHEDULED`), `organizer_id`; unlisted token backend-only (not on read DTO)
- [x] 1.2 New `rpc/organizer/v1/concert_service.proto` — `ConcertService` (bare verbs) `Create`, `Update`, `Cancel`, `Publish`, `UploadCoverImage`, `RegenerateToken`, `List` + messages + error docs; keep identity `OrganizerService` unchanged
- [x] 1.3 `buf lint`/`format`/`breaking`; spec PR merge → Release → BSR gen — shipped v0.56.0 (spec #874)

## 2. Cloud-provisioning

- [x] 2.1 Private GCS bucket `…-organizer-media` + external HTTPS LB + Cloud CDN backend bucket + URL-map `/cdn/*` path matcher; grant LB service account `storage.objectViewer` and backend GSA `objectAdmin` (no `allUsers`) (Pulumi) — Cert Manager DNS-01 + Cloudflare A(proxied:false); `ORGANIZER_MEDIA_CDN_BASE` in dev/prod ConfigMap. Shipped #460–#463; DRS relaxed by an out-of-band org-admin override (roles/orgpolicy.policyAdmin is org-level only, so not Pulumi-managed)

## 3. Backend

- [x] 3.1 Atlas migration: `series` columns (description, visibility, publish_state, organizer_id FK, unlisted_token, domain-specific `*_at`; **no `cover_image_url`** — cover is a media relationship, see 3.1a); index for state/visibility filtering
- [x] 3.1a Atlas migration: `media` (`id` UUIDv7 PK, `organizer_id` FK, `kind` enum = `IMAGE` only, `attributes` JSONB) + `series_media` join (`series_id` FK, `media_id` FK, `display_order`, PK(series_id, media_id)); split from / supersede the combined `series_media` (forward-only `20260827000000`); no stored `object_key`/`created_at` (derived)
- [x] 3.2 Authoring usecase: create draft (Series+Event(s)+performers) reusing the **fix-series-fragmentation shared series-resolution helper** + `resolveOrCreateVenue` + natural-key event upsert (NOT the removed AdoptStaged path); ownership check vs represented artists; validation (title/date required, open≤start, future date)
- [x] 3.3 List own concerts (drafts + published); edit draft; edit published (correction, no re-notify); `Cancel` (mark CANCELLED — terminal, drop from fan surfaces, **emit `CONCERT.cancelled`** for consumers/caches)
- [x] 3.4 `Publish`: emit **one `CONCERT.created` per series** (carrying the published events' ids) for PUBLIC only; DRAFT/UNLISTED never emit; publishing a new event under an already-published series emits once for the new event id(s)
- [x] 3.5 Supersede in publish txn: drop matching `staged_concert`; **claim** an already-published discovered event (re-point to organizer's series, keep id, mark organizer-owned, no re-emit); **do not resurrect a suppressed slot** without explicit action; route a **different-organizer** slot to admin reconciliation (no auto takeover)
- [x] 3.6 Discovery exclusion in the cron: filter `FollowRepo.ListAll` by Organizer↔Artist association **before** `SearchNewConcerts` (skip the Gemini call); resumes on disassociate/deactivate
- [x] 3.7 Unlisted token: HMAC sign on publish + `RegenerateToken`; shared guard excludes DRAFT/UNLISTED/CANCELLED from all list/discovery/follower/notify queries. **DEFERRED:** the fan-facing public read path (a `GetUnlisted` RPC + verify-on-read) — see 4.2; ships in a follow-up
- [x] 3.8 Cover-image upload → GCS `cdn/{org}/{media_id}` with server-side type/size validation → create `media` + `series_media` rows; read URL derived from the key (`{CDN_BASE}/cdn/{org}/{media_id}`), same in every state (MVP: drafts also under `cdn/`, obscurity-protected); no `internal/`/signed-URL/publish-copy in MVP (deferred to extensions)
- [x] 3.9 Emit `organizer.concert.published` analytics event
- [x] 3.10 `ConcertService` authoring handlers behind org-scoped authorization
- [x] 3.11 Unit tests: ownership reject, notify-once/never (draft+unlisted), merge-supersede no double-notify, association exclusion on/off, draft/unlisted/cancelled never leak, token verify+regenerate, cancel; `make check` with upgraded BSR

## 4. Frontend (organizer console)

- [x] 4.1 Authoring screens: create/edit draft (title, description, date, open/start, venue, performers from `ListArtists`), cover upload, visibility, Publish; list own concerts; edit-published + Cancel — shipped #573 (**PUBLIC-only** MVP, no UNLISTED/share-token UI)
- [x] 4.2 Unlisted-event public route that validates the tokenized URL — **DESCOPED** from this change (removed from the spec delta): needs a fan-facing `GetUnlisted` RPC + public read path that do not exist yet; ships in a dedicated follow-up change
- [x] 4.3 `make check` with upgraded BSR

## 5. Release & ship to prod

- [x] 5.1 Backend PR merged (#418) → release **v1.48.0** → prod pin bump (media rework + #414 discovery fix); prod pods on v1.48.0
- [x] 5.2 Frontend PR merged (#573) → release **v1.61.0** (authoring UI shipped to prod; PUBLIC-only MVP)
- [x] 5.3 Cloud-provisioning PRs merged (#460–#463) → `pulumi up` applied (v234 succeeded): private bucket + LB + Cloud CDN backend bucket + `/cdn/*` + IAM grants; media cert ACTIVE
- [x] 5.4 Verify in prod — **INFRA + code verified**: CDN serves a real object over `https://media.liverty-music.app/cdn/…` = 200 (private bucket, no `allUsers`); backend on v1.48.0 (discovery #414 fix live); frontend authoring UI on v1.61.0. **DEFERRED to organic use** (precedent: `auto-publish-new-concerts` 4.2/4.3): the full authenticated authoring→publish→notify→supersede flow is confirmed at the code/infra layer and left for the first real organizer to exercise (needs an org session + represented artist + a discovered record to supersede). UNLISTED verification is out of scope (descoped, see 4.2)
