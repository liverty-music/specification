## REMOVED Requirements

### Requirement: Organizer uploads a cover image

**Reason**: Renamed and reworked into an async, direct-to-storage media pipeline
(see the ADDED requirements below). The synchronous "API receives bytes → writes
one object → serves a single URL" behavior no longer holds.

**Migration**: Superseded by "Organizer uploads an image" + "Uploaded images are
processed into safe, responsive variants" in this same capability. No data
migration — the authoring image feature is not yet live in prod, so there is no
existing image to convert; the series image field becomes `Series.media` of type
`entity.v1.Media`.

## ADDED Requirements

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

## MODIFIED Requirements

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
