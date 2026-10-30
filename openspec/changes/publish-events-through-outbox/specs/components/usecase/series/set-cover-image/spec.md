## MODIFIED Requirements

### Requirement: Record and hand over for processing

SetCoverImage SHALL record the SeriesImage as an IMAGE of the caller's Organizer for the Series together with the request to process it for the Series (SeriesImage.Create); the Series' current cover SHALL stay until processing succeeds. Repeating SetCoverImage for the same SeriesImage SHALL succeed and hand over nothing new, whether or not the image was processed. When the SeriesImage cannot be recorded, SetCoverImage SHALL fail with the error of SeriesImage.Create (Unavailable when the processing request cannot be recorded), so the member can repeat it.

#### Scenario: Cover replaced later
- **WHEN** the owner attaches a new image to a Series that has a cover
- **THEN** the Series still shows its old cover until the new image is processed

#### Scenario: Repeated attach
- **WHEN** the same SeriesImage is attached twice
- **THEN** both calls succeed, one SeriesImage is recorded and it is processed once

#### Scenario: Announcement fails
- **WHEN** SeriesImage.Create fails with Unavailable because the processing request cannot be recorded
- **THEN** SetCoverImage fails with Unavailable, nothing is recorded, and repeating it after the failure records the SeriesImage and hands it over for processing

#### Scenario: Repeated attach after processing
- **WHEN** the owner attaches a SeriesImage again after it was processed into the Series' cover
- **THEN** SetCoverImage succeeds and the image is not processed again

### Requirement: Only the caller's own upload

SetCoverImage SHALL accept a SeriesImage only when SeriesImage.OriginalExists reports the original under the caller's Organizer, or when SeriesImage.Get finds the SeriesImage already recorded for the caller's Organizer. Otherwise it SHALL fail, recording nothing and handing nothing over: with PermissionDenied when the SeriesImage is recorded for another Organizer, and with FailedPrecondition when no such SeriesImage was uploaded.

#### Scenario: Another Organizer's series image id
- **WHEN** a member attaches, to their own Series, the SeriesImage id of another Organizer's cover
- **THEN** SetCoverImage fails with PermissionDenied and neither Series' cover changes

#### Scenario: Nothing uploaded
- **WHEN** a member attaches a SeriesImage id for which no original was uploaded
- **THEN** SetCoverImage fails with FailedPrecondition and nothing is recorded
