## 1. Backend — one-time listed_venue_name normalization migration

- [ ] 1.1 Write a Go migration job (or Atlas migration) that iterates over all rows in `staged_concerts` and `concerts` (or the equivalent table) where `listed_venue_name IS NOT NULL`, applies `entity.NormalizeVenueName`, and updates the row in place
- [ ] 1.2 Run the migration against the production DB and verify row counts and sample values

## 2. Backend — listed_venue_name normalization before storage

- [ ] 2.1 In `internal/usecase/concert_creation_uc.go`, apply `entity.NormalizeVenueName(sc.ListedVenueName)` before assigning to `StagedConcert.ListedVenueName`
- [ ] 2.2 Verify existing unit tests for `concert_creation_uc.go` still pass; update any test fixtures that assert the raw (unnormalized) listed venue name

## 3. Backend — languageCode in Google Places API

- [ ] 3.1 Add a `countryCodeToLanguage(cc string) string` helper function (in `internal/infrastructure/maps/google/` or `internal/entity/`) implementing the static country → BCP 47 map (`JP→ja`, `KR→ko`, `CN→zh-CN`, `TW→zh-TW`, default `en`)
- [ ] 3.2 Add `LanguageCode string` field to `textSearchRequest` struct in `internal/infrastructure/maps/google/client.go`
- [ ] 3.3 In `SearchPlace`, extract the country code from `adminArea` (split on `"-"`, take first element) and pass `countryCodeToLanguage(country)` as `LanguageCode` in the request body
- [ ] 3.4 Add unit tests for `countryCodeToLanguage` covering `JP`, `KR`, `CN`, `TW`, empty string, and unknown country code

## 4. Frontend — locale-aware venue name in concert mapper

- [ ] 4.1 Identify how the concert mapper is currently called (function vs class, where `currentLanguage` is available) by reading `src/adapter/rpc/mapper/concert-mapper.ts` and its call sites
- [ ] 4.2 Add a `lang: string` parameter to the concert mapper (function signature or constructor/method) and thread it from `UserStore.currentLanguage` at the call site(s)
- [ ] 4.3 Replace the unconditional `venue?.name?.value ?? listedVenueName?.value` expression with locale-aware selection: `ja` prefers `listed_venue_name`, `en` prefers `venue.name`, with cross-fallback
- [ ] 4.4 Update or add unit tests for the concert mapper covering: ja with both fields, ja with only venue.name, en with both fields, en with only listed_venue_name

## 5. Verification

- [ ] 5.1 Run `make check` in the backend repo and confirm all tests pass
- [ ] 5.2 Run `make check` in the frontend repo and confirm all tests pass
- [ ] 5.3 Open the dashboard as a Japanese user and confirm a Mrs. Green Apple (or similar Japanese artist) tour shows Japanese venue names on event cards and detail sheets
- [ ] 5.4 Ship to prod
