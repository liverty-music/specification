## ADDED Requirements

### Requirement: Hype-lane matching

The `entities/concert.ts` file SHALL export an `isHypeMatched(hype: HypeLevel, lane: LaneType): boolean` pure function that determines whether a user's hype level qualifies a concert for display in a given proximity lane. The matching rule is: a hype level matches a lane if the hype's ordinal value is greater than or equal to the lane's ordinal value, where the ordering is `watch=0 < home=1 < nearby=2 < away=3` for hype and `home=1 < nearby=2 < away=3` for lanes.

#### Scenario: Away hype matches all lanes

- **WHEN** `isHypeMatched('away', 'home')` is called
- **THEN** it returns `true`

#### Scenario: Home hype matches home lane only

- **WHEN** `isHypeMatched('home', 'home')` is called
- **THEN** it returns `true`

#### Scenario: Home hype does not match nearby lane

- **WHEN** `isHypeMatched('home', 'nearby')` is called
- **THEN** it returns `false`

#### Scenario: Watch hype matches no lanes

- **WHEN** `isHypeMatched('watch', 'home')` is called
- **THEN** it returns `false`

#### Scenario: Nearby hype matches home and nearby

- **WHEN** `isHypeMatched('nearby', 'home')` and `isHypeMatched('nearby', 'nearby')` are called
- **THEN** both return `true`

#### Scenario: Nearby hype does not match away

- **WHEN** `isHypeMatched('nearby', 'away')` is called
- **THEN** it returns `false`

---

### Requirement: Follow deduplication check

The `entities/follow.ts` file SHALL export a `hasFollow(follows: ReadonlyArray<{ artist: { id: string } }>, artistId: string): boolean` pure function that returns `true` if any element in the array has a matching artist ID. This function enforces the business invariant that a user cannot follow the same artist twice.

#### Scenario: Artist already followed

- **WHEN** `hasFollow([{ artist: { id: 'a1' } }], 'a1')` is called
- **THEN** it returns `true`

#### Scenario: Artist not followed

- **WHEN** `hasFollow([{ artist: { id: 'a1' } }], 'a2')` is called
- **THEN** it returns `false`

#### Scenario: Empty follow list

- **WHEN** `hasFollow([], 'a1')` is called
- **THEN** it returns `false`

---

### Requirement: Onboarding step progression

The `entities/onboarding.ts` file SHALL export:
1. An `OnboardingStep` constant object with values: `lp`, `discovery`, `dashboard`, `detail`, `my-artists`, `completed`.
2. A `STEP_ORDER` array defining the canonical progression order.
3. A `stepIndex(step: OnboardingStepValue): number` pure function returning the ordinal position of a step in `STEP_ORDER`.
4. An `isOnboarding(step: OnboardingStepValue): boolean` pure function returning `true` for steps `discovery`, `dashboard`, `detail`, `my-artists`.
5. An `isCompleted(step: OnboardingStepValue): boolean` pure function returning `true` only for `completed`.

#### Scenario: stepIndex returns correct ordinal

- **WHEN** `stepIndex('discovery')` is called
- **THEN** it returns `1`

#### Scenario: stepIndex for first step

- **WHEN** `stepIndex('lp')` is called
- **THEN** it returns `0`

#### Scenario: isOnboarding for active step

- **WHEN** `isOnboarding('dashboard')` is called
- **THEN** it returns `true`

#### Scenario: isOnboarding for terminal steps

- **WHEN** `isOnboarding('lp')` and `isOnboarding('completed')` are called
- **THEN** both return `false`

#### Scenario: isCompleted for completed step

- **WHEN** `isCompleted('completed')` is called
- **THEN** it returns `true`

#### Scenario: isCompleted for non-completed step

- **WHEN** `isCompleted('dashboard')` is called
- **THEN** it returns `false`

---

### Requirement: Onboarding step normalization

The `entities/onboarding.ts` file SHALL export a `normalizeStep(raw: string): OnboardingStepValue` pure function that converts a raw string (potentially a legacy numeric step index) into a valid `OnboardingStepValue`. If the raw value is a legacy numeric index (`'0'`-`'7'`), it SHALL be mapped to the corresponding step. If the raw value is already a valid step string, it SHALL be returned as-is. If the raw value is unrecognized, it SHALL return `'lp'` as the fallback.

#### Scenario: Legacy numeric step '1' maps to discovery

- **WHEN** `normalizeStep('1')` is called
- **THEN** it returns `'discovery'`

#### Scenario: Legacy numeric step '7' maps to completed

- **WHEN** `normalizeStep('7')` is called
- **THEN** it returns `'completed'`

#### Scenario: Valid string step passes through

- **WHEN** `normalizeStep('dashboard')` is called
- **THEN** it returns `'dashboard'`

#### Scenario: Unknown value falls back to lp

- **WHEN** `normalizeStep('invalid')` is called
- **THEN** it returns `'lp'`

---

### Requirement: Location code decomposition

The `entities/user.ts` file SHALL export a `codeToHome(code: string): { countryCode: string; level1: string }` pure function that decomposes an ISO 3166-2 subdivision code into a structured home object. The country code SHALL be extracted from the first two characters of the input.

#### Scenario: Japanese prefecture code

- **WHEN** `codeToHome('JP-13')` is called
- **THEN** it returns `{ countryCode: 'JP', level1: 'JP-13' }`

#### Scenario: US state code

- **WHEN** `codeToHome('US-CA')` is called
- **THEN** it returns `{ countryCode: 'US', level1: 'US-CA' }`

---

### Requirement: Location display name

The `entities/user.ts` file SHALL export a `displayName(code: string, lang?: 'ja' | 'en'): string` pure function that returns the human-readable name for an ISO 3166-2 code. If no entry is found for the code, the code itself SHALL be returned. The default language SHALL be `'ja'`.

#### Scenario: Known Japanese prefecture in Japanese

- **WHEN** `displayName('JP-13')` is called
- **THEN** it returns `'東京都'`

#### Scenario: Known Japanese prefecture in English

- **WHEN** `displayName('JP-13', 'en')` is called
- **THEN** it returns `'Tokyo'`

#### Scenario: Unknown code returns code as fallback

- **WHEN** `displayName('XX-99')` is called
- **THEN** it returns `'XX-99'`

---

### Requirement: Merkle path binary conversions

The `entities/entry.ts` file SHALL export pure conversion functions for Merkle proof data:
1. `bytesToHex(bytes: Uint8Array): string` — converts bytes to lowercase hex string.
2. `bytesToDecimal(bytes: Uint8Array): string` — converts bytes to decimal string via hex intermediate.
3. `uuidToFieldElement(uuid: string): string` — strips hyphens from a UUID and converts the hex to a decimal string.

#### Scenario: bytesToHex converts bytes

- **WHEN** `bytesToHex(new Uint8Array([0x0a, 0xff]))` is called
- **THEN** it returns `'0aff'`

#### Scenario: bytesToHex empty input

- **WHEN** `bytesToHex(new Uint8Array([]))` is called
- **THEN** it returns `''`

#### Scenario: bytesToDecimal converts to decimal string

- **WHEN** `bytesToDecimal(new Uint8Array([0x01, 0x00]))` is called
- **THEN** it returns `'256'`

#### Scenario: bytesToDecimal empty input returns zero

- **WHEN** `bytesToDecimal(new Uint8Array([]))` is called
- **THEN** it returns `'0'`

#### Scenario: uuidToFieldElement strips hyphens

- **WHEN** `uuidToFieldElement('550e8400-e29b-41d4-a716-446655440000')` is called
- **THEN** it returns the decimal representation of `0x550e8400e29b41d4a716446655440000`
