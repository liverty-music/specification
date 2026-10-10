## ADDED Requirements

### Requirement: Only the caller's own upload

AttachMedia SHALL accept a Media only when Media.OriginalExists reports the original under the caller's Organizer, or when Media.FindMediaByID finds the Media already recorded for the caller's Organizer. Otherwise it SHALL fail, recording and announcing nothing: with PermissionDenied when the Media is recorded for another Organizer, and with FailedPrecondition when no such Media was uploaded.

#### Scenario: Another organizer's media id
- **WHEN** an operator attaches, to their own Series, the Media id of another Organizer's cover
- **THEN** AttachMedia fails with PermissionDenied and neither Series' cover changes

#### Scenario: Nothing uploaded
- **WHEN** an operator attaches a Media id for which no original was uploaded
- **THEN** AttachMedia fails with FailedPrecondition and nothing is recorded

## MODIFIED Requirements

### Requirement: Record and hand over for processing

AttachMedia SHALL record the Media as an IMAGE of the caller's Organizer (Media.InsertMedia) and announce the upload for the Series so it is processed; the Series' current cover SHALL stay until processing succeeds. Repeating AttachMedia for the same Media SHALL succeed: it announces again while the original is still uploaded, and announces nothing once the original was processed. When the announcement fails, AttachMedia SHALL fail with Unavailable, so the operator can repeat it.

#### Scenario: Cover replaced later
- **WHEN** the owner attaches a new image to a Series that has a cover
- **THEN** the Series still shows its old cover until the new image is processed

#### Scenario: Repeated attach
- **WHEN** the same Media is attached twice
- **THEN** both calls succeed and one Media is recorded

#### Scenario: Announcement fails
- **WHEN** the processing announcement cannot be published
- **THEN** AttachMedia fails with Unavailable, and repeating it after the failure announces the upload

#### Scenario: Repeated attach after processing
- **WHEN** the owner attaches a Media again after it was processed into the Series' cover
- **THEN** AttachMedia succeeds and nothing is announced
