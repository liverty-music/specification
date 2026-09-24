<!-- merge_group: LOGO-ANALYSIS | target: components/usecase/artist/sync-artist-image | members: 2 -->
<!-- renamed_scenarios: 0 -->

### Requirement: Logo Color Analysis and Sync Pipeline Integration

The system SHALL analyze artist logo images (clearLOGO PNGs) to extract
dominant color properties. The analysis SHALL decode the PNG, iterate all
non-transparent pixels (alpha >= 10), convert each pixel from sRGB to OKLCH
color space, and classify pixels as chromatic (chroma > 0.04) or achromatic.
The fanart sync pipeline (CronJob and ARTIST.created consumer) SHALL perform
this logo color analysis after fetching fanart data, using the best logo
image selected by highest likes count from `HDMusicLogo`, falling back to
`MusicLogo` if `HDMusicLogo` is empty.

#### Scenario: Chromatic logo (e.g., colored text/symbol)
- **WHEN** a logo image has more than 30% of non-transparent pixels with OKLCH chroma > 0.04
- **THEN** the analysis SHALL return `isChromatic = true`, `dominantHue` as the peak of a 36-bin (10° each) hue histogram, and `dominantLightness` as the mean lightness of all non-transparent pixels

#### Scenario: Achromatic light logo (e.g., white text)
- **WHEN** a logo image has 30% or fewer chromatic pixels and a mean lightness > 0.6
- **THEN** the analysis SHALL return `isChromatic = false`, `dominantHue` absent (not set), and `dominantLightness` reflecting the high lightness value

#### Scenario: Achromatic dark logo (e.g., black text)
- **WHEN** a logo image has 30% or fewer chromatic pixels and a mean lightness ≤ 0.6
- **THEN** the analysis SHALL return `isChromatic = false`, `dominantHue` absent (not set), and `dominantLightness` reflecting the low lightness value

#### Scenario: Fully transparent image
- **WHEN** a logo image has no non-transparent pixels (alpha >= 10)
- **THEN** the analysis SHALL return nil (no analysis possible)

#### Scenario: Artist has HDMusicLogo
- **WHEN** fanart data is fetched and HDMusicLogo contains images
- **THEN** the sync pipeline SHALL download the best HDMusicLogo image (by likes), run color analysis, and store the result in the `logoColorProfile` field of the fanart JSONB

#### Scenario: Artist has only MusicLogo
- **WHEN** fanart data is fetched and HDMusicLogo is empty but MusicLogo contains images
- **THEN** the sync pipeline SHALL download the best MusicLogo image and run color analysis

#### Scenario: Artist has no logo images
- **WHEN** fanart data is fetched but neither HDMusicLogo nor MusicLogo contain images
- **THEN** the sync pipeline SHALL store fanart data without a `logoColorProfile` field

#### Scenario: Logo image download fails
- **WHEN** the logo image HTTP request fails or returns non-200
- **THEN** the sync pipeline SHALL log a warning and store fanart data without a `logoColorProfile` field (non-fatal)
