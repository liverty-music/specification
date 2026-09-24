# Replace a concert cover image

## Purpose

An organizer uploads an image and makes it the cover of its concert, without the concert ever showing a broken or unprocessed image.

## Requirements

### Requirement: Upload, attach, process

An image uploaded with the authorization from MediaUseCase.CreateMediaUploadURL and attached with MediaUseCase.AttachMedia SHALL become the concert's cover once ProcessMedia has produced its variants, and the previous cover SHALL be served until then and deleted afterwards.

#### Scenario: New cover on a published concert
- **WHEN** an organizer uploads and attaches a JPEG to a published concert with a cover
- **THEN** fans see the old cover until the new variants are ready, then the new cover

#### Scenario: Unsupported image
- **WHEN** the uploaded file is not a supported image
- **THEN** the concert keeps its previous cover
