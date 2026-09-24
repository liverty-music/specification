# Attach Media

## Purpose

AttachMedia lets the owning organizer operator record an uploaded image as the next cover of one of its concerts (Series). The image becomes the cover only once it has been processed into servable variants.

## Requirements

### Requirement: Ids required

AttachMedia SHALL fail with InvalidArgument when the Series id or the Media id is empty.

#### Scenario: Missing media id
- **WHEN** AttachMedia is called with no Media id
- **THEN** it fails with InvalidArgument

### Requirement: Only the owner

AttachMedia SHALL fail with PermissionDenied, without revealing whether the Series exists, when the Series does not exist or is not owned by the caller's Organizer. A Series in any publish state SHALL be accepted.

#### Scenario: Another organizer's series
- **WHEN** an operator attaches an image to another Organizer's Series
- **THEN** AttachMedia fails with PermissionDenied and nothing is recorded

### Requirement: Record and hand over for processing

AttachMedia SHALL record the Media as an IMAGE of the caller's Organizer (Media.InsertMedia) and announce the upload for the Series so it is processed; the Series' current cover SHALL stay until processing succeeds. Repeating AttachMedia for the same Media SHALL succeed. A failed announcement SHALL NOT fail AttachMedia.

#### Scenario: Cover replaced later
- **WHEN** the owner attaches a new image to a Series that has a cover
- **THEN** the Series still shows its old cover until the new image is processed

#### Scenario: Repeated attach
- **WHEN** the same Media is attached twice
- **THEN** both calls succeed and one Media is recorded
