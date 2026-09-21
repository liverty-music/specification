<!-- merge_group: ARTIST-IMAGE-SELECT | target: components/entity/artist | members: 2 -->

<!-- member: artist-image | flags: CLASSNAME -->
### Requirement: Best Image Selection
The system SHALL provide a `BestByLikes` function that selects the image with the highest `Likes` count from a given `FanartImage` slice. The function SHALL return an empty string when the input slice is empty.

#### Scenario: Multiple images with different likes
- **WHEN** `BestByLikes` is called with a slice containing images with likes values [3, 7, 1]
- **THEN** the function SHALL return the URL of the image with 7 likes

#### Scenario: Empty image slice
- **WHEN** `BestByLikes` is called with an empty slice
- **THEN** the function SHALL return an empty string

<!-- member: artist-image | flags: CLASSNAME -->
### Requirement: Fanart Proto Mapper
The mapper layer SHALL convert the domain `Fanart` entity (with full image arrays) to the proto `Fanart` message (with single best URL per type) using `BestByLikes` for selection. The mapper SHALL also convert the domain `LogoColorProfile` to the proto `LogoColorProfile` message when present.

#### Scenario: Mapper selects best images
- **WHEN** a domain Artist with Fanart data is mapped to proto
- **THEN** each proto Fanart field SHALL contain the URL of the image with the highest likes count from the corresponding domain field

#### Scenario: Mapper includes logo analysis
- **WHEN** a domain Artist with Fanart and LogoColorProfile is mapped to proto
- **THEN** the proto Fanart message SHALL include the `logo_color_profile` field with dominant hue, lightness, and chromaticity

