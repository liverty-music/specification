## MODIFIED Requirements

### Requirement: Frontend Background Color Derivation
The frontend SHALL use `LogoColorProfile` data to determine the card background `--artist-hue` custom property. When `dominantHue` is present (chromatic logos), the hue SHALL be set to the complementary angle (`(dominantHue + 180) % 360`) to ensure the logo color contrasts with the background. When `dominantHue` is absent (achromatic logos), the hue SHALL fall back to the existing name-hash algorithm. When no `LogoColorProfile` is available, the existing name-hash algorithm SHALL be used unchanged.

#### Scenario: Chromatic logo card background
- **WHEN** an event card renders for an artist with `dominantHue` present and set to `335` (pink)
- **THEN** `--artist-hue` SHALL be set to `155` (complementary green, calculated as `(335 + 180) % 360`)

#### Scenario: Chromatic logo with red hue
- **WHEN** an event card renders for an artist with `dominantHue` present and set to `29` (red)
- **THEN** `--artist-hue` SHALL be set to `209` (complementary cyan, calculated as `(29 + 180) % 360`)

#### Scenario: Chromatic logo with hue above 180
- **WHEN** an event card renders for an artist with `dominantHue` present and set to `260` (blue-purple)
- **THEN** `--artist-hue` SHALL be set to `80` (complementary yellow-green, calculated as `(260 + 180) % 360`)

#### Scenario: Achromatic light logo card background
- **WHEN** an event card renders for an artist with `dominantHue` absent and `dominantLightness = 0.85`
- **THEN** `--artist-hue` SHALL be set to the name-hash value

#### Scenario: Achromatic dark logo card background
- **WHEN** an event card renders for an artist with `dominantHue` absent and `dominantLightness = 0.15`
- **THEN** `--artist-hue` SHALL be set to the name-hash value

#### Scenario: No logo analysis available
- **WHEN** an event card renders for an artist without `LogoColorProfile`
- **THEN** `--artist-hue` SHALL be computed from the artist name hash (existing behavior)
