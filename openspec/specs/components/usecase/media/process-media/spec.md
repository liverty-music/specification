# Process Media

## Purpose

ProcessMedia turns an attached image into the safe, servable cover of its Series, triggered when an upload is announced: it checks the image, produces the thumbnail and large variants, switches the Series' cover to them, and reclaims the replaced cover and the original upload.

## Requirements

### Requirement: Triggered by an upload announcement

ProcessMedia SHALL run once for each announced upload, with its Media and Series. A transient failure SHALL cause the same upload to be processed again; every step SHALL be safe to repeat. When the Media no longer exists, the upload SHALL be ignored.

#### Scenario: Media gone
- **WHEN** the announced Media no longer exists (Media.FindMediaByID NotFound)
- **THEN** nothing is processed

#### Scenario: Storage briefly unavailable
- **WHEN** reading the original upload fails
- **THEN** the upload is processed again later

### Requirement: Only safe images become variants

ProcessMedia SHALL accept a JPEG, PNG or WebP original whose width and height are each at most 8000 px and whose pixel count is at most 50,000,000, checked before the image is fully decoded. It SHALL remove all embedded metadata, including EXIF, and produce WebP variants at most 800 px wide (thumb) and at most 1920 px wide (large), keeping the aspect ratio without cropping. Any other original — including an SVG or corrupt file — SHALL produce no variants, SHALL have its original deleted, SHALL NOT be retried, and SHALL leave the Series' cover unchanged; the organizer can upload again.

#### Scenario: Valid photo
- **WHEN** a 4000×3000 JPEG is processed
- **THEN** an 800 px wide thumb and a 1920 px wide large WebP are produced without EXIF

#### Scenario: WebP original
- **WHEN** a 4000×3000 WebP is processed
- **THEN** an 800 px wide thumb and a 1920 px wide large WebP are produced without EXIF, the same as for JPEG or PNG

#### Scenario: Decompression bomb
- **WHEN** an image declares 10000×10000 pixels
- **THEN** it is rejected before full decoding, no variant exists, and it is not retried

### Requirement: Cover switched only after variants exist

After both variants are stored, ProcessMedia SHALL make the Media the Series' cover (Media.CutOverSeriesMedia); until then the previous cover SHALL keep being served. Only after the switch SHALL the previous cover's variants be deleted; a failure to delete them SHALL NOT fail processing. When the Series no longer exists, the original SHALL be deleted and the cover left as is.

#### Scenario: Replacing a published cover
- **WHEN** a new image is processed for a Series with a cover
- **THEN** the old variants are served until the new ones are the cover, and are deleted afterwards

#### Scenario: Series deleted meanwhile
- **WHEN** the Series no longer exists at the switch
- **THEN** the original is deleted and processing ends

### Requirement: Original is not kept

After a successful switch, ProcessMedia SHALL delete the original upload; the original SHALL never be served.

#### Scenario: After processing
- **WHEN** processing completes
- **THEN** only the thumb and large variants remain for the Media
