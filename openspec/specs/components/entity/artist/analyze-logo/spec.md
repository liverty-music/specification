# Artist.AnalyzeLogo

## Purpose

Computes the logo color profile of a logo image: whether it is colored, its dominant hue, and its mean lightness.

## Requirements

### Requirement: AnalyzeLogo measures only visible pixels
AnalyzeLogo SHALL count a pixel only when its opacity is at least 10 on a 0 to 255 scale, and SHALL measure each counted pixel's chroma, lightness and hue in the OKLCH perceptual color space. When no pixel is counted, AnalyzeLogo SHALL return no profile.

#### Scenario: Fully transparent image
- **WHEN** every pixel of the image has an opacity below 10
- **THEN** AnalyzeLogo returns no profile

#### Scenario: Faint pixels ignored
- **WHEN** an image has red pixels at opacity 5 and white pixels at full opacity
- **THEN** the profile is computed from the white pixels only

### Requirement: AnalyzeLogo classifies the logo as chromatic or achromatic
A counted pixel SHALL be chromatic when its chroma is above 0.04. The logo SHALL be chromatic when at least 30% of the counted pixels are chromatic, and achromatic otherwise. dominant_lightness SHALL be the mean lightness of all counted pixels.

#### Scenario: Mostly colored logo
- **WHEN** 60% of the counted pixels have a chroma above 0.04
- **THEN** the profile is chromatic

#### Scenario: Exactly 30% colored
- **WHEN** exactly 30% of the counted pixels have a chroma above 0.04
- **THEN** the profile is chromatic

#### Scenario: Mostly gray logo
- **WHEN** 10% of the counted pixels have a chroma above 0.04
- **THEN** the profile is not chromatic and has no dominant_hue

#### Scenario: Lightness is the mean
- **WHEN** half the counted pixels have lightness 1 and half have lightness 0
- **THEN** dominant_lightness is 0.5

### Requirement: AnalyzeLogo finds the dominant hue band
For a chromatic logo, AnalyzeLogo SHALL sort the chromatic pixels into 36 hue bands of 10 degrees each and SHALL set dominant_hue to the center of the most populated band; when several bands are equally populated, the band with the lowest hue SHALL win.

#### Scenario: One dominant band
- **WHEN** most chromatic pixels have hues between 20 and 30 degrees
- **THEN** dominant_hue is 25

#### Scenario: Tied bands
- **WHEN** the bands 120 to 130 degrees and 240 to 250 degrees hold equally many chromatic pixels and no band holds more
- **THEN** dominant_hue is 125
