## ADDED Requirements

### Requirement: Artist color derivation

The `adapter/view/artist-color.ts` file SHALL export pure functions for deriving deterministic colors from artist data:
1. `artistHue(name: string): number` — computes a stable hue (0-359) from the artist name using a hash function.
2. `artistColor(name: string): string` — returns an HSL color string with fixed saturation and lightness.
3. `artistHueFromColorProfile(profile: LogoColorProfile | undefined, artistName: string): number` — returns the profile's `dominantHue` when `isChromatic` is true and `dominantHue` is defined, otherwise falls back to `artistHue(artistName)`.

These functions SHALL NOT depend on any framework, DI container, or DOM API.

#### Scenario: Same name produces same hue

- **WHEN** `artistHue('Radiohead')` is called twice
- **THEN** both calls return the same number

#### Scenario: Hue is within valid range

- **WHEN** `artistHue('any artist name')` is called
- **THEN** the result is between 0 and 359 inclusive

#### Scenario: artistColor returns HSL string

- **WHEN** `artistColor('Radiohead')` is called
- **THEN** it returns a string matching the pattern `hsl(<number>, <number>%, <number>%)`

#### Scenario: Chromatic profile uses dominant hue

- **WHEN** `artistHueFromColorProfile({ isChromatic: true, dominantHue: 120, dominantLightness: 50 }, 'Radiohead')` is called
- **THEN** it returns `120`

#### Scenario: Achromatic profile falls back to name hash

- **WHEN** `artistHueFromColorProfile({ isChromatic: false, dominantHue: 120, dominantLightness: 50 }, 'Radiohead')` is called
- **THEN** it returns the same value as `artistHue('Radiohead')`

#### Scenario: Undefined profile falls back to name hash

- **WHEN** `artistHueFromColorProfile(undefined, 'Radiohead')` is called
- **THEN** it returns the same value as `artistHue('Radiohead')`

---

### Requirement: Hype display metadata

The `adapter/view/hype-display.ts` file SHALL export a `HYPE_TIERS` constant mapping each `Hype` value to its display label key and icon string. The mapping SHALL cover all four hype values: `watch`, `home`, `nearby`, `away`.

This constant SHALL NOT depend on any framework, DI container, or DOM API.

#### Scenario: All hype values have entries

- **WHEN** `HYPE_TIERS` is accessed
- **THEN** it has entries for keys `'watch'`, `'home'`, `'nearby'`, `'away'`

#### Scenario: Each entry has label and icon

- **WHEN** `HYPE_TIERS['home']` is accessed
- **THEN** it contains `labelKey` (non-empty string) and `icon` (non-empty string) properties
