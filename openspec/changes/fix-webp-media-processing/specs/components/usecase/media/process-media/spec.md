# Spec Delta

## MODIFIED Requirements

### Requirement: Only safe images become variants

ProcessMedia SHALL accept a JPEG, PNG or WebP original whose width and height are each at most 8000 px and whose pixel count is at most 50,000,000, checked before the image is fully decoded. It SHALL remove all embedded metadata, including EXIF, and produce WebP variants at most 800 px wide (thumb) and at most 1920 px wide (large), keeping the aspect ratio without cropping. Any other original — including an SVG or corrupt file — SHALL produce no variants, SHALL have its original deleted, SHALL NOT be retried, and SHALL leave the Series' cover unchanged; the organizer can upload again.

#### Scenario: Valid photo
- **WHEN** a 4000×3000 JPEG is processed
- **THEN** an 800 px wide thumb and a 1920 px wide large WebP are produced without EXIF

#### Scenario: WebP original
- **WHEN** a WebP image is processed
- **THEN** an 800 px wide thumb and a 1920 px wide large WebP are produced without EXIF, the same as for JPEG or PNG

#### Scenario: Decompression bomb
- **WHEN** an image declares 10000×10000 pixels
- **THEN** it is rejected before full decoding, no variant exists, and it is not retried
