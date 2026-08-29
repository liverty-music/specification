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
original is retained only until processing completes.

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

#### Scenario: Only the owning organizer can attach an image

- **WHEN** an organizer requests an image upload for a concert they do not own
- **THEN** the system SHALL deny it without revealing the concert's existence

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
one; when a new image becomes the concert's image, the previously served
variants SHALL be reclaimed (deleted) so stale objects do not accumulate.

#### Scenario: New image supersedes and reclaims the old

- **WHEN** an organizer uploads a replacement image for a concert that already
  has one
- **THEN** the concert SHALL reference the new image's variants and the previous
  image's served variants SHALL be deleted
