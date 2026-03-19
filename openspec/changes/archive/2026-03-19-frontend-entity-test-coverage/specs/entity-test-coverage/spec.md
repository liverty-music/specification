## ADDED Requirements

### Requirement: isHypeMatched exhaustive coverage
`isHypeMatched(hype, lane)` SHALL be tested for all 12 combinations of HypeLevel x LaneType using table-driven tests.

#### Scenario: Full matrix via it.each
- **WHEN** every (hype, lane) pair is evaluated
- **THEN** results match the rule `HYPE_ORDER[hype] >= LANE_ORDER[lane]`

### Requirement: hasFollow boundary cases
`hasFollow()` SHALL be tested for multi-element lists and duplicate artist IDs.

#### Scenario: Artist found among multiple follows
- **WHEN** follows contains 3 entries and the target is the last one
- **THEN** returns true

#### Scenario: Duplicate artist IDs in list
- **WHEN** follows contains two entries with the same artist ID
- **THEN** returns true

### Requirement: normalizeStep full legacy mapping
`normalizeStep()` SHALL be tested for every key in the legacy numeric migration table plus gap values.

#### Scenario: All mapped numeric values
- **WHEN** input is `'0'`, `'1'`, `'3'`, `'4'`, `'5'`, or `'7'`
- **THEN** returns the corresponding OnboardingStepValue

#### Scenario: Unmapped numeric gap values
- **WHEN** input is `'2'` or `'6'`
- **THEN** returns `'lp'` (fallback)

### Requirement: translationKey coverage
`translationKey()` SHALL have dedicated tests covering known codes and unknown codes.

#### Scenario: Known prefecture code
- **WHEN** code is `'JP-13'`
- **THEN** returns `'tokyo'`

#### Scenario: Unknown code fallback
- **WHEN** code is `'XX-99'`
- **THEN** returns `'XX-99'`

### Requirement: codeToHome boundary cases
`codeToHome()` SHALL be tested for short input strings.

#### Scenario: Code shorter than 3 characters
- **WHEN** code is `'JP'` (no hyphen or subdivision)
- **THEN** returns `{ countryCode: 'JP', level1: 'JP' }` without throwing

### Requirement: bytesToHex zero-padding
`bytesToHex()` SHALL verify that single-digit hex values are zero-padded.

#### Scenario: Leading zero byte
- **WHEN** input is `[0x00]`
- **THEN** returns `'00'`

### Requirement: bytesToDecimal multi-byte
`bytesToDecimal()` SHALL be tested with 3+ byte inputs.

#### Scenario: Three-byte input
- **WHEN** input is `[0x01, 0x00, 0x00]`
- **THEN** returns `'65536'`

### Requirement: uuidToFieldElement robustness
`uuidToFieldElement()` SHALL handle already-stripped and non-standard inputs.

#### Scenario: UUID without hyphens
- **WHEN** input is `'550e8400e29b41d4a716446655440000'`
- **THEN** returns the same decimal as the hyphenated form

### Requirement: artistHue empty string
`artistHue()` SHALL handle empty string input without throwing.

#### Scenario: Empty string input
- **WHEN** name is `''`
- **THEN** returns a number in 0-359 range

### Requirement: artistHueFromColorProfile dominantHue zero
`artistHueFromColorProfile()` SHALL treat `dominantHue === 0` as valid chromatic, not as falsy fallback.

#### Scenario: Chromatic profile with hue 0 (red)
- **WHEN** profile is `{ isChromatic: true, dominantHue: 0, dominantLightness: 50 }`
- **THEN** returns `0` (not the name-hash fallback)

### Requirement: HYPE_TIERS completeness
`HYPE_TIERS` SHALL have an entry for every value of the `Hype` union type.

#### Scenario: All hype values present
- **WHEN** checking keys of `HYPE_TIERS`
- **THEN** keys include `'watch'`, `'home'`, `'nearby'`, `'away'`

#### Scenario: Each entry has labelKey and icon
- **WHEN** iterating all entries
- **THEN** every entry has non-empty `labelKey` and non-empty `icon`

### Requirement: HYPE_ORDER and LANE_ORDER completeness
Exported order constants SHALL cover every value of their respective union types.

#### Scenario: HYPE_ORDER keys match HypeLevel
- **WHEN** checking keys of `HYPE_ORDER`
- **THEN** keys are exactly `['watch', 'home', 'nearby', 'away']`

#### Scenario: LANE_ORDER keys match LaneType
- **WHEN** checking keys of `LANE_ORDER`
- **THEN** keys are exactly `['home', 'nearby', 'away']`
