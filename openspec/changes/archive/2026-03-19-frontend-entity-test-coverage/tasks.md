## 1. Entity layer tests

- [x] 1.1 `concert.spec.ts`: Add `HYPE_ORDER` / `LANE_ORDER` completeness tests; convert `isHypeMatched` to `it.each` table-driven style covering all 12 combinations
- [x] 1.2 `follow.spec.ts`: Add multi-element list test and duplicate artist ID test
- [x] 1.3 `onboarding.spec.ts`: Add `normalizeStep` tests for all legacy numeric keys (`'3'`, `'4'`, `'5'`) and gap values (`'2'`, `'6'`)
- [x] 1.4 `user.spec.ts`: Add `translationKey()` tests (known code, unknown fallback); add `codeToHome()` short-input boundary test
- [x] 1.5 `entry.spec.ts`: Add `bytesToHex` zero-padding test (`0x00`); `bytesToDecimal` 3-byte test; `uuidToFieldElement` hyphen-free input test

## 2. View adapter tests

- [x] 2.1 `artist-color.spec.ts`: Add `artistHue` empty-string test; add `artistHueFromColorProfile` `dominantHue === 0` boundary test
- [x] 2.2 Create `hype-display.spec.ts`: Completeness test (all Hype keys present), each entry has non-empty `labelKey` and `icon`

## 3. Verification

- [x] 3.1 Run `make check` and fix any issues
