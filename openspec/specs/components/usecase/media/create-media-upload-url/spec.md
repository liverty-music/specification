# Create Media Upload Url

## Purpose

CreateMediaUploadURL gives an organizer operator an authorization, valid for 15 minutes, to upload one image (JPEG, PNG or WebP, at most 10 MiB) directly to storage, together with the Media id used to attach it to a concert afterwards.

## Requirements

### Requirement: Supported image types only

CreateMediaUploadURL SHALL accept the content types image/jpeg, image/png and image/webp, ignoring case and surrounding spaces, and SHALL fail with InvalidArgument for any other type.

#### Scenario: Upper-case type
- **WHEN** the declared type is " IMAGE/PNG "
- **THEN** an upload authorization is returned

#### Scenario: SVG
- **WHEN** the declared type is image/svg+xml
- **THEN** CreateMediaUploadURL fails with InvalidArgument

### Requirement: Short-lived, size-limited authorization

CreateMediaUploadURL SHALL mint a new Media id and return an authorization valid for 15 minutes to upload exactly one object of the declared type and at most 10 MiB, scoped to the caller's Organizer, together with the Media id and the 10 MiB limit. No concert is named at this step and nothing is stored. When upload storage is not available it SHALL fail with Internal.

#### Scenario: Authorization issued
- **WHEN** an operator asks to upload a JPEG
- **THEN** an authorization valid for 15 minutes, a new Media id and a 10 MiB limit are returned

#### Scenario: Upload over the limit
- **WHEN** the operator uploads 11 MiB with the authorization
- **THEN** storage refuses the upload
