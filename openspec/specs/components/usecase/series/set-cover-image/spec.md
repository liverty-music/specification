# Set Cover Image

## Purpose

SetCoverImage lets the owning organizer operator record an uploaded image as the next cover of one of its concerts (Series). The image becomes the cover only once it has been processed into servable variants.

## Requirements

### Requirement: Ids required

SetCoverImage SHALL fail with InvalidArgument when the Series id or the SeriesImage id is empty.

#### Scenario: Missing series image id
- **WHEN** SetCoverImage is called with no SeriesImage id
- **THEN** it fails with InvalidArgument

### Requirement: Only the owner

SetCoverImage SHALL fail with PermissionDenied, without revealing whether the Series exists, when the Series does not exist or is not owned by the caller's Organizer. A Series in any publish state SHALL be accepted.

#### Scenario: Another organizer's series
- **WHEN** an operator attaches an image to another Organizer's Series
- **THEN** SetCoverImage fails with PermissionDenied and nothing is recorded

### Requirement: Record and hand over for processing

SetCoverImage SHALL record the SeriesImage as an IMAGE of the caller's Organizer (SeriesImage.Create) and announce the upload for the Series so it is processed; the Series' current cover SHALL stay until processing succeeds. Repeating SetCoverImage for the same SeriesImage SHALL succeed. A failed announcement SHALL NOT fail SetCoverImage.

#### Scenario: Cover replaced later
- **WHEN** the owner attaches a new image to a Series that has a cover
- **THEN** the Series still shows its old cover until the new image is processed

#### Scenario: Repeated attach
- **WHEN** the same SeriesImage is attached twice
- **THEN** both calls succeed and one SeriesImage is recorded
