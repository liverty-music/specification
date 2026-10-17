# Regenerate Share Url

## Purpose

RegenerateShareUrl lets a member of the owning Organizer replace the share token of an UNLISTED concert, so the previous share link stops working.

## Requirements

### Requirement: Only the owner

RegenerateShareUrl SHALL fail with PermissionDenied, without revealing whether the Series exists, when the Series does not exist or is not owned by the caller's Organizer.

#### Scenario: Another Organizer's series
- **WHEN** a member regenerates the token of another Organizer's Series
- **THEN** RegenerateShareUrl fails with PermissionDenied

### Requirement: Unlisted only

RegenerateShareUrl SHALL fail with FailedPrecondition when the Series' visibility is not UNLISTED.

#### Scenario: Public series
- **WHEN** the owner regenerates the token of a PUBLIC Series
- **THEN** RegenerateShareUrl fails with FailedPrecondition

### Requirement: New random token

RegenerateShareUrl SHALL give the Series a new random share token (Series.SetUnlistedToken) and return it; the previous token SHALL no longer open the Series.

#### Scenario: Token rotated
- **WHEN** the owner regenerates the token of an UNLISTED Series
- **THEN** a new token is returned and the old one no longer opens the Series
