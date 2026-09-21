# Create Media Upload Url

## Purpose

Lets a vetted organizer author and publish first-party concert event pages
for the artists it represents, as informational pages that supersede
scraped data and take those artists out of the discovery pipeline.

## Requirements

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
