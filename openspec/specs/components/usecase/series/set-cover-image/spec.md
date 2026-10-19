# Set Cover Image

## Purpose

SetCoverImage lets a member of the owning Organizer record an uploaded image as the next cover of one of its concerts (Series). The image becomes the cover only once it has been processed into servable variants.

## Requirements

### Requirement: Ids required

SetCoverImage SHALL fail with InvalidArgument when the Series id or the SeriesImage id is empty.

#### Scenario: Missing series image id
- **WHEN** SetCoverImage is called with no SeriesImage id
- **THEN** it fails with InvalidArgument

### Requirement: Only the owner

SetCoverImage SHALL fail with PermissionDenied, without revealing whether the Series exists, when the Series does not exist or is not owned by the caller's Organizer. A Series in any publish state SHALL be accepted.

#### Scenario: Another Organizer's series
- **WHEN** a member attaches an image to another Organizer's Series
- **THEN** SetCoverImage fails with PermissionDenied and nothing is recorded

### Requirement: Record and hand over for processing

SetCoverImage SHALL record the SeriesImage as an IMAGE of the caller's Organizer (SeriesImage.Create) and announce the upload for the Series so it is processed; the Series' current cover SHALL stay until processing succeeds. Repeating SetCoverImage for the same SeriesImage SHALL succeed: it announces again while the original is still uploaded, and announces nothing once the original was processed. When the announcement fails, SetCoverImage SHALL fail with Unavailable, so the member can repeat it.

#### Scenario: Cover replaced later
- **WHEN** the owner attaches a new image to a Series that has a cover
- **THEN** the Series still shows its old cover until the new image is processed

#### Scenario: Repeated attach
- **WHEN** the same SeriesImage is attached twice
- **THEN** both calls succeed and one SeriesImage is recorded

#### Scenario: Announcement fails
- **WHEN** the processing announcement cannot be published
- **THEN** SetCoverImage fails with Unavailable, and repeating it after the failure announces the upload

#### Scenario: Repeated attach after processing
- **WHEN** the owner attaches a SeriesImage again after it was processed into the Series' cover
- **THEN** SetCoverImage succeeds and nothing is announced

### Requirement: Only the caller's own upload

SetCoverImage SHALL accept a SeriesImage only when SeriesImage.OriginalExists reports the original under the caller's Organizer, or when SeriesImage.Get finds the SeriesImage already recorded for the caller's Organizer. Otherwise it SHALL fail, recording and announcing nothing: with PermissionDenied when the SeriesImage is recorded for another Organizer, and with FailedPrecondition when no such SeriesImage was uploaded.

#### Scenario: Another Organizer's series image id
- **WHEN** a member attaches, to their own Series, the SeriesImage id of another Organizer's cover
- **THEN** SetCoverImage fails with PermissionDenied and neither Series' cover changes

#### Scenario: Nothing uploaded
- **WHEN** a member attaches a SeriesImage id for which no original was uploaded
- **THEN** SetCoverImage fails with FailedPrecondition and nothing is recorded
