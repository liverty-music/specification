# organizer-event-authoring Specification

## Purpose

Lets a vetted organizer author and publish first-party concert event pages
for the artists it represents, as informational pages that supersede
scraped data and take those artists out of the discovery pipeline.
## Requirements
### Requirement: Organizer authors a concert as a draft

The system SHALL let an authenticated organizer operator create a concert —
a `Series` (title, type, `description`, an optional image exposed as a `media`
object — see "Organizer uploads an image") with one or
more `Event`s (venue, local date, open/start time) and an artist lineup —
scoped to artists the organizer represents. Times are recorded at the
**`Event` (performance) level**; a multi-showtime day (e.g. 昼の部/夜の部)
is modeled as multiple `Event`s under one `Series`. A newly created concert
SHALL be `DRAFT` and SHALL NOT appear in any public list or notification
until published. Creation SHALL validate that a title and each event's date
are present, that open time (when given) is not after start time, and that
the date is not in the past.

#### Scenario: Create a draft concert for a represented artist

- **WHEN** an organizer operator creates a concert naming an artist the
  organizer represents
- **THEN** the system SHALL persist it as `DRAFT` owned by that organizer
- **AND** the concert SHALL NOT appear in discovery, follower lists, or
  notifications

#### Scenario: Multi-showtime day is multiple events

- **WHEN** an organizer authors two showtimes on the same date at the same
  venue
- **THEN** the system SHALL persist two `Event`s (distinct start times)
  under one `Series`

#### Scenario: Cannot author for an unrepresented artist

- **WHEN** an organizer operator creates a concert naming an artist the
  organizer does not represent
- **THEN** the system SHALL reject it with a permission-denied error

#### Scenario: Venue is resolved to the shared venue entity

- **WHEN** a concert is authored with a venue name/address
- **THEN** the system SHALL resolve it to an existing `Venue` (or create
  one) via the shared Places get-or-create path, not a free-text duplicate

### Requirement: Organizer lists and edits its own concerts

The system SHALL let an organizer operator list the concerts its organizer
owns (both `DRAFT` and `PUBLISHED`) and edit them. A `DRAFT` is fully
editable. A `PUBLISHED` concert MAY be edited for corrections (e.g. time,
venue, description) and MAY be **cancelled**; a cancelled concert SHALL stop
appearing to fans and SHALL be marked cancelled rather than silently
deleted. Cancellation SHALL emit a cancellation signal (`CONCERT.cancelled`)
so downstream consumers and fan caches drop it. `CANCELLED` is **terminal**:
to run the concert again the organizer authors a new concert (no
un-cancel/re-publish of a cancelled one).

#### Scenario: Organizer sees its own drafts and published concerts

- **WHEN** an organizer operator lists concerts
- **THEN** the system SHALL return only concerts owned by that organizer,
  including drafts

#### Scenario: Correcting a published concert

- **WHEN** the owning organizer edits a published concert's time or venue
- **THEN** the change SHALL be reflected on the public page without
  re-emitting a new-concert notification

#### Scenario: Cancelling a published concert

- **WHEN** the owning organizer cancels a published concert
- **THEN** the concert SHALL be marked cancelled and SHALL stop appearing in
  discovery and follower lists
- **AND** the system SHALL emit `CONCERT.cancelled` so consumers/caches drop
  it

#### Scenario: Cancelled is terminal

- **WHEN** an organizer wants to run a cancelled concert again
- **THEN** the system SHALL require authoring a new concert (a `CANCELLED`
  concert SHALL NOT be re-published)

### Requirement: Publish makes a concert live, first-party, and notifies once

The system SHALL let the owning organizer publish a `DRAFT` concert. On
publish a `PUBLIC` concert becomes `PUBLISHED` and the system SHALL emit
**one `CONCERT.created` per series**, carrying the ids of the events being
published (consistent with the series-grouped publish-once model), which
drives the existing follower notification. `DRAFT` and `UNLISTED` concerts
SHALL NOT emit `CONCERT.created`. A concert first published as `UNLISTED`
and later changed to `PUBLIC` SHALL emit `CONCERT.created` at that **first
transition to `PUBLIC`**, idempotently — never more than once for the same
events (subsequent visibility toggles do not re-notify). Only the owning
organizer may publish.

#### Scenario: Unlisted later made public notifies exactly once

- **WHEN** an `UNLISTED` published concert is changed to `PUBLIC`
- **THEN** the system SHALL emit `CONCERT.created` once at that transition
- **AND** SHALL NOT emit it again for the same events on any later toggle

#### Scenario: Public publish notifies once per series

- **WHEN** the owning organizer publishes a `PUBLIC` series with one or more
  events
- **THEN** the series SHALL become `PUBLISHED` and emit exactly one
  `CONCERT.created` carrying those events' ids

#### Scenario: Adding a new event to a published series notifies once for it

- **WHEN** the owning organizer publishes an additional event under an
  already-`PUBLISHED` series
- **THEN** the system SHALL emit one `CONCERT.created` for the series
  carrying only the new event id(s), and SHALL NOT re-announce the
  previously-published events

#### Scenario: Unlisted or draft never notifies

- **WHEN** a concert is saved as `DRAFT` or published as `UNLISTED`
- **THEN** the system SHALL NOT emit `CONCERT.created` and followers SHALL
  NOT be notified

#### Scenario: Only the owning organizer may publish

- **WHEN** an operator of a different organizer attempts to publish the
  concert
- **THEN** the system SHALL reject it with a permission-denied error

### Requirement: Publish enforces the complete required-field set

Publish SHALL be the **final server-side gate** on a concert going live: the
system SHALL validate the complete required-field set at publish time and
reject an incomplete concert regardless of how the draft reached its current
state (author, edit, or partial data). Creation validates a subset for an
early-feedback draft, but a draft MAY still be missing later-required data;
publish SHALL re-validate the whole set so no `PUBLISHED` concert is ever
surfaced with a missing required field. The required set is:

- a non-empty **title**;
- **at least one performing artist**;
- **at least one event**, and **every** event SHALL have a **non-empty venue**
  and a **valid local date**.

`description` and `media` remain **optional** and SHALL NOT block publish. On a
failed check the concert SHALL remain `DRAFT` (the state is unchanged, no
`CONCERT.created` is emitted) and the system SHALL reject the request with a
failed-precondition error naming the missing requirement. This gate is
independent of ownership and slot-conflict checks (those still apply).

#### Scenario: Publish rejects a concert missing a required field

- **WHEN** the owning organizer publishes a `DRAFT` concert that has no
  performing artist, or an event with no venue, or is otherwise missing a
  required field
- **THEN** the system SHALL reject the publish with a failed-precondition error
  naming the missing requirement, the concert SHALL remain `DRAFT`, and no
  `CONCERT.created` SHALL be emitted

#### Scenario: Publish succeeds when the required set is complete

- **WHEN** the owning organizer publishes a `DRAFT` concert with a title, at
  least one performer, and at least one event that has a venue and a valid date
- **THEN** the system SHALL publish it (subject to the ownership and
  slot-conflict rules), even when `description` and `media` are absent

### Requirement: First-party publish supersedes scraped data without harm

Organizer-authored events insert under the organizer's own `series_id`
(resolved via the shared series-resolution path), converging on the event
natural key `(venue, local_date, start)`. On publishing a `PUBLIC` concert
whose slot matches existing data, the first-party record SHALL become
authoritative:

- A matching pending `staged_concert` SHALL be dropped.
- A matching **already-published discovered event** SHALL be **claimed** —
  the event is re-pointed to the organizer's series and marked
  organizer-owned, keeping its event id so user references (e.g. ticket
  journeys) are preserved; `CONCERT.created` SHALL NOT be re-emitted for an
  event that was already announced.
- A matching **suppressed** slot SHALL NOT be silently resurrected;
  publishing into a suppressed slot SHALL require an explicit, logged
  organizer action.
- A slot already owned by a **different organizer's** first-party series
  SHALL be treated as a conflict routed to admin reconciliation, NOT an
  automatic ownership overwrite.

#### Scenario: Supersede a pending staged concert

- **WHEN** publish matches a `staged_concert` at the same slot
- **THEN** the staged row SHALL be dropped and the first-party concert
  published

#### Scenario: Claim an already-published discovered event

- **WHEN** publish matches an already-published discovered event at the same
  slot
- **THEN** the system SHALL re-point that event to the organizer's series,
  keep its id, mark it organizer-owned, and SHALL NOT re-emit
  `CONCERT.created`

#### Scenario: Suppressed slot is not silently resurrected

- **WHEN** publish targets a slot in the suppression set
- **THEN** the system SHALL NOT auto-publish it and SHALL require an explicit
  organizer action to proceed

#### Scenario: Cross-organizer slot is a conflict, not a takeover

- **WHEN** publish matches a slot already owned by a different organizer's
  first-party series
- **THEN** the system SHALL route it to admin reconciliation and SHALL NOT
  reassign ownership automatically

### Requirement: Represented artists are excluded from scraping

While an artist is associated with an organizer, the system SHALL exclude
that artist from concert-search scraping (first-party is authoritative). The
exclusion SHALL be keyed on the **Organizer↔Artist association**, not on the
existence of a published concert: associating an artist starts the
exclusion, and disassociating it (or deactivating the organizer) resumes
scraping.

#### Scenario: Associated artist is excluded from discovery scraping

- **WHEN** the discovery pipeline runs for an artist associated with an
  active organizer
- **THEN** the system SHALL skip scraping that artist's concerts

#### Scenario: Disassociation resumes scraping

- **WHEN** an artist is disassociated from its organizer (or the organizer
  is deactivated)
- **THEN** the system SHALL resume scraping that artist's concerts

### Requirement: Visibility controls where a published concert appears

A published concert SHALL have a visibility of `PUBLIC` or `UNLISTED`.
`PUBLIC` concerts appear in normal discovery and follower lists. `UNLISTED`
concerts SHALL be excluded from discovery, follower lists, and notifications,
and SHALL carry a regenerable signed token (the owning organizer can
regenerate it). The fan-facing read path that resolves that token to view an
`UNLISTED` concert (a public `GetUnlisted` RPC + route) is a follow-up and is
NOT part of this change's MVP.

#### Scenario: Public concert appears in discovery

- **WHEN** a `PUBLIC` concert is published
- **THEN** it SHALL appear in discovery and to followers per existing rules

#### Scenario: Unlisted concert is excluded from fan-facing surfaces

- **WHEN** an `UNLISTED` concert is published
- **THEN** it SHALL NOT appear in discovery, lists, or notifications
- **AND** its signed token SHALL be stored and regenerable by the owning
  organizer (the token-resolving public read path ships in a follow-up)

### Requirement: Organizer uploads an image

The system SHALL let the organizer attach a single image to a concert via a
**direct-to-storage upload**: the system issues a short-lived, single-object
upload authorization scoped to the caller's organization and a fixed content
type, the client uploads the original bytes directly to object storage, and the
client then notifies the system to record the image and begin processing. The
system SHALL validate the declared content type and enforce a maximum byte size
at authorization time. A concert MAY be published without an image. The uploaded
original is retained only until processing finishes — it is reclaimed on both
successful processing and permanent failure; an upload that is authorized but
never attached is a rare orphan (no automatic cleanup at MVP).

#### Scenario: Image is stored and served

- **WHEN** an organizer requests to upload an image of a supported type (JPEG,
  PNG, or WebP) for a concert they own
- **THEN** the system SHALL return a short-lived upload authorization and a media
  identifier, and — once the client confirms the upload — record the image as
  belonging to that concert, process it asynchronously (see "Uploaded images are
  processed into safe, responsive variants"), and serve the resulting variants

#### Scenario: Invalid image is rejected

- **WHEN** an organizer requests an upload for an unsupported content type, or
  the uploaded object exceeds the maximum byte size
- **THEN** the system SHALL reject it (invalid-argument at authorization; the
  storage upload itself SHALL reject an over-size object)

#### Scenario: Only the owning organizer can attach an image to a concert

- **WHEN** an organizer attempts to attach an uploaded image to a concert they
  do not own (the attach step carries the concert; the upload-authorization step
  does not)
- **THEN** the system SHALL deny the attach without revealing the concert's
  existence

### Requirement: Uploaded images are processed into safe, responsive variants

After an original is uploaded, the system SHALL asynchronously process it before
serving: it SHALL verify the actual image content (not merely the declared
type), reject images whose pixel dimensions exceed a safe limit **before** full
decoding (decompression-bomb defense), remove all embedded metadata (EXIF), and
produce responsive next-generation-format (WebP) variants — a thumbnail and a
large size — served publicly via the CDN with long-lived immutable caching. The
served image SHALL be represented as a media object exposing the variant URLs.
The system SHALL NOT serve the unprocessed original.

#### Scenario: A valid image becomes servable variants

- **WHEN** processing completes for a valid uploaded image
- **THEN** the system SHALL make thumbnail and large WebP variants available at
  stable CDN URLs with EXIF removed, and the concert's `media` SHALL expose those
  variant URLs

#### Scenario: A malformed or oversized-dimension image yields no variants

- **WHEN** the uploaded bytes are not a valid supported image, or exceed the
  pixel/dimension limit
- **THEN** the system SHALL not produce variants and SHALL not retry
  indefinitely; the image simply does not become available and the organizer can
  re-upload

#### Scenario: Readiness is observable without a stored status

- **WHEN** an image has been uploaded but processing is not yet complete
- **THEN** the served variant URLs SHALL not yet resolve, and the organizer
  console MAY show an optimistic local preview until the variants become
  available (no processing-status field is exposed)

### Requirement: Replacing an image reclaims the previous one

The system SHALL let an organizer replace a concert's image by uploading a new
one; the previously served variants SHALL be reclaimed (deleted) so stale objects
do not accumulate, but ONLY after the replacement's variants exist, so an
already-published concert never serves a broken image during a replace.

#### Scenario: New image supersedes and reclaims the old without a gap

- **WHEN** an organizer replaces the image of an already-published concert
- **THEN** the concert SHALL keep serving the old variants until the new variants
  are ready, then reference the new variants, and only then SHALL the previous
  variants be deleted

