## Why

`organizer-event-authoring` (②) ships the **minimal** informational event
page. Competitor parity (tiget / LivePocket / Peatix / e+ / ぴあ) and real
organizer needs call for richer authoring: media, streaming events, the
JP-idiomatic fields (注意事項 / 問い合わせ先 / 年齢制限), password-protected
pages, per-event notes, and lineup roles. This follow-on **captures that
deferred scope in one place** so it is not lost; it is implemented when
demand appears (not part of the M1 milestone). Tracked by
liverty-music/specification#759. Ticketing stays in ④; sub-owner/co-organizer
RBAC stays in `organizer-rbac-subowners`.

## What Changes

Extends the `organizer-event-authoring` capability with:
- **Media**: multiple cover images / gallery; YouTube (video) embed;
  external links (official site / SNS).
- **Streaming as a first-class mode**: `venue` / `online` / `hybrid`, with a
  stream method/URL (Liverty-attendable-concert MVP was venue-only).
- **Discovery metadata**: category/genre + search keywords.
- **JP-idiomatic structured fields**: 注意事項 (notices/terms), 問い合わせ先
  (contact: built-in form or email/phone/URL), 年齢制限 (age restriction).
- **Password-protected visibility**: in addition to `PUBLIC` / `UNLISTED`.
- **Per-event description**: date-specific notes (MVP had one Series-level
  description).
- **Lineup detail**: performer order + role (headliner / opening act /
  guest).
- **Scheduled publish**: `publish_at` (publish at a future time), beyond the
  MVP draft→publish toggle.

## Capabilities

### New Capabilities
<!-- None. -->

### Modified Capabilities
- `organizer-event-authoring`: adds the richer authoring requirements above
  on top of the MVP capability created by change ②.

## Impact

- **specification**: additive fields on `series.proto` / `event.proto` /
  `event_performers` (images, video_url, links, stream mode+url, category,
  keywords, notices, contact, age_restriction, password hash, per-event
  description, performer role+order, publish_at) + authoring RPC fields. All
  additive/non-breaking.
- **backend**: field persistence + validation; streaming-mode handling;
  password-gate on the read path; scheduled-publish job; lineup ordering.
- **frontend**: richer organizer console authoring form (media uploader,
  streaming toggle, structured fields, password option, lineup editor,
  schedule picker).
- **cloud-provisioning**: larger/gallery image storage if needed.
- **Non-goals:** ticketing (④); co-organizer / sub-owner RBAC
  (`organizer-rbac-subowners`); congratulatory flowers / face-auth /
  blocklist (not planned).
