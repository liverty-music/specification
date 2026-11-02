# Process

## Purpose

Process turns an attached image into the safe, servable cover of its Series, run for each processing request SeriesImage.Create records: it checks the image, produces the thumbnail and large variants, switches the Series' cover to them, and reclaims the replaced cover and the original upload.

## Requirements

### Requirement: Only safe images become variants

Process SHALL accept a JPEG, PNG or WebP original whose width and height are each at most 8000 px and whose pixel count is at most 50,000,000, checked before the image is fully decoded. It SHALL remove all embedded metadata, including EXIF, and produce WebP variants at most 800 px wide (thumb) and at most 1920 px wide (large), keeping the aspect ratio without cropping. Any other original — including an SVG or corrupt file — SHALL produce no variants, SHALL have its original deleted, SHALL NOT be retried, and SHALL leave the Series' cover unchanged; a member can upload again.

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

After both variants are stored, Process SHALL make the SeriesImage the Series' cover (SeriesImage.ReplaceCover); until then the previous cover SHALL keep being served. Only after the switch SHALL the previous cover's variants be deleted; a failure to delete them SHALL NOT fail processing. When the Series no longer exists, the original SHALL be deleted and the cover left as is.

#### Scenario: Replacing a published cover
- **WHEN** a new image is processed for a Series with a cover
- **THEN** the old variants are served until the new ones are the cover, and are deleted afterwards

#### Scenario: Series deleted meanwhile
- **WHEN** the Series no longer exists at the switch
- **THEN** the original is deleted and processing ends

### Requirement: Original is not kept

After a successful switch, Process SHALL delete the original upload; the original SHALL never be served.

#### Scenario: After processing
- **WHEN** processing completes
- **THEN** only the thumb and large variants remain for the SeriesImage

### Requirement: Runs for each recorded processing request

Process SHALL run for each processing request recorded by SeriesImage.Create, with that SeriesImage and the Series the request names. A transient failure SHALL cause the same SeriesImage to be processed again; every step SHALL be safe to repeat, so a request delivered twice leaves one processed cover. When the SeriesImage no longer exists, nothing SHALL be processed.

#### Scenario: SeriesImage uploaded
- **WHEN** SeriesImage.Create records a request to process a SeriesImage for Series S
- **THEN** Process runs for that SeriesImage and Series S

#### Scenario: Delivered twice
- **WHEN** the same processing request is delivered twice
- **THEN** the Series has one cover made from that SeriesImage

#### Scenario: SeriesImage gone
- **WHEN** the SeriesImage no longer exists (SeriesImage.Get NotFound)
- **THEN** nothing is processed

#### Scenario: Storage briefly unavailable
- **WHEN** reading the original upload fails
- **THEN** the SeriesImage is processed again later
