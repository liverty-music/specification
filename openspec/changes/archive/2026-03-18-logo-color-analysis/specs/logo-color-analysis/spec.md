## ADDED Requirements

### Requirement: Logo Color Extraction
The system SHALL analyze artist logo images (clearLOGO PNGs) to extract dominant color properties. The analysis SHALL decode the PNG, iterate all non-transparent pixels (alpha >= 10), convert each pixel from sRGB to OKLCH color space, and classify pixels as chromatic (chroma > 0.04) or achromatic.

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

### Requirement: sRGB to OKLCH Conversion
The system SHALL convert sRGB pixel values to OKLCH color space using fixed-coefficient matrix math (sRGB → Linear RGB → OKLab → OKLCH). The conversion SHALL use Go standard library types (`color.NRGBA`) with no external dependencies.

#### Scenario: Pure white pixel
- **WHEN** sRGB (255, 255, 255) is converted to OKLCH
- **THEN** lightness SHALL be approximately 1.0 and chroma SHALL be approximately 0.0

#### Scenario: Pure red pixel
- **WHEN** sRGB (255, 0, 0) is converted to OKLCH
- **THEN** lightness SHALL be approximately 0.63, chroma SHALL be > 0.2, and hue SHALL be approximately 29°

#### Scenario: Pure black pixel
- **WHEN** sRGB (0, 0, 0) is converted to OKLCH
- **THEN** lightness SHALL be approximately 0.0 and chroma SHALL be approximately 0.0

### Requirement: Logo Analysis Integration in Sync Pipeline
The fanart sync pipeline (CronJob and ARTIST.created consumer) SHALL perform logo color analysis after fetching fanart data. The analysis SHALL use the best logo image selected by `BestByLikes` from `HDMusicLogo`, falling back to `MusicLogo` if `HDMusicLogo` is empty.

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

### Requirement: LogoColorProfile Proto Message
The system SHALL define a `LogoColorProfile` protobuf message within `liverty_music.entity.v1` containing `dominant_hue` (optional float, 0-360, present only for chromatic logos), `dominant_lightness` (float, 0-1), and `is_chromatic` (bool). The `Fanart` message SHALL include an `optional LogoColorProfile logo_color_profile` field.

#### Scenario: Artist with logo analysis data
- **WHEN** an Artist with logo analysis is serialized to proto
- **THEN** the `fanart.logo_color_profile` field SHALL contain a `LogoColorProfile` message with the extracted values

#### Scenario: Artist without logo analysis data
- **WHEN** an Artist without logo analysis is serialized to proto
- **THEN** the `fanart.logo_color_profile` field SHALL be absent (optional not set)

### Requirement: Frontend Background Color Derivation
The frontend SHALL use `LogoColorProfile` data to determine the card background `--artist-hue` custom property. When `dominantHue` is present (chromatic logos), the hue SHALL be set to that value (logo's own hue family). When `dominantHue` is absent (achromatic logos), the hue SHALL fall back to the existing name-hash algorithm. When no `LogoColorProfile` is available, the existing name-hash algorithm SHALL be used unchanged.

#### Scenario: Chromatic logo card background
- **WHEN** an event card renders for an artist with `dominantHue` present and set to `0` (red)
- **THEN** `--artist-hue` SHALL be set to `0` (same hue family as the logo, with low-chroma background per CSS)

#### Scenario: Achromatic light logo card background
- **WHEN** an event card renders for an artist with `dominantHue` absent and `dominantLightness = 0.85`
- **THEN** `--artist-hue` SHALL be set to the name-hash value and background lightness SHALL remain dark (logo is light, background is dark for contrast)

#### Scenario: Achromatic dark logo card background
- **WHEN** an event card renders for an artist with `dominantHue` absent and `dominantLightness = 0.15`
- **THEN** `--artist-hue` SHALL be set to the name-hash value and background lightness SHALL be raised to ensure the dark logo is visible

#### Scenario: No logo analysis available
- **WHEN** an event card renders for an artist without `LogoColorProfile`
- **THEN** `--artist-hue` SHALL be computed from the artist name hash (existing behavior)
