<!-- merge_group: ARTIST-IMAGE-SELECT | target: components/entity/artist | members: 2 -->
<!-- renamed_scenarios: 0 -->

### Requirement: Fanart Image Selection and Mapping

The system SHALL select, for each fanart image type, the image with the
highest likes count from the available images of that type, returning an
empty string when no images are available for that type. When mapping the
domain `Fanart` entity (with full image arrays) to the proto `Fanart` message
(with a single best-by-likes URL per image type), the system SHALL apply this
selection for every image field. The system SHALL also convert the domain
`LogoColorProfile` to the proto `LogoColorProfile` message when present.

#### Scenario: Multiple images with different likes
- **WHEN** images with likes values [3, 7, 1] are available for selection
- **THEN** the function SHALL return the URL of the image with 7 likes

#### Scenario: Empty image slice
- **WHEN** no images are available for selection
- **THEN** the function SHALL return an empty string

#### Scenario: Mapper selects best images
- **WHEN** a domain Artist with Fanart data is mapped to proto
- **THEN** each proto Fanart field SHALL contain the URL of the image with the highest likes count from the corresponding domain field

#### Scenario: Mapper includes logo analysis
- **WHEN** a domain Artist with Fanart and LogoColorProfile is mapped to proto
- **THEN** the proto Fanart message SHALL include the `logo_color_profile` field with dominant hue, lightness, and chromaticity
