# Attach Media

## Purpose

Lets a vetted organizer author and publish first-party concert event pages
for the artists it represents, as informational pages that supersede
scraped data and take those artists out of the discovery pipeline.

## Requirements

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
