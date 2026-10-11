# Spec Delta

## Purpose

The organizer-facing SeriesImage service boundary: an operator asks for an authorization to upload one image for a concert cover, acting for their own Organizer.

## ADDED Requirements

### Requirement: CreateUploadUrl acts for the caller's own active Organizer

CreateUploadUrl SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's tenant. A failure of ResolveCaller SHALL be returned unchanged and no upload is authorized: PermissionDenied when no Organizer is linked to the tenant or the Organizer is provisioning, without revealing whether an Organizer exists, and FailedPrecondition when the Organizer is deactivated. CreateUploadUrl SHALL then return what SeriesImageUseCase.CreateUploadUrl returns for the declared content type: the upload authorization, its size limit and the SeriesImage id that SeriesService.SetCoverImage takes as `series_image_id`.

#### Scenario: Operator of an active Organizer asks to upload

- **WHEN** an operator of an active Organizer calls CreateUploadUrl for a PNG
- **THEN** the response carries an upload authorization and a new SeriesImage id

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** CreateUploadUrl fails with FailedPrecondition and no upload is authorized
