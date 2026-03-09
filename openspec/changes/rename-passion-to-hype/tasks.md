## 1. Specification (Proto)

- [x] 1.1 Rename `PassionLevel` enum to `HypeType` in `entity/v1/artist.proto` with values: UNSPECIFIED=0, WATCH=1, HOME=2, NEARBY=3, ANYWHERE=4
- [x] 1.2 Rename `FollowedArtist.passion_level` field to `hype` (type `HypeType`) in `rpc/artist/v1/artist_service.proto`
- [x] 1.3 Rename `SetPassionLevel` RPC to `SetHype`, rename request/response messages (`SetHypeRequest`, `SetHypeResponse`) in `rpc/artist/v1/artist_service.proto`
- [x] 1.4 Update proto comments/documentation to reflect Hype terminology
- [x] 1.5 Run `buf lint` and `buf format -w` to validate

## 2. Backend — Database Migration

- [x] 2.1 Create migration to rename `passion_level` column to `hype` on `followed_artists` table
- [x] 2.2 Map existing values: `must_go` → `anywhere`, `local_only` → `anywhere`, `keep_an_eye` → `watch`
- [x] 2.3 Drop old CHECK constraint, add new: `hype IN ('watch', 'home', 'nearby', 'anywhere')`
- [x] 2.4 Change DEFAULT from `'local_only'` to `'anywhere'`
- [x] 2.5 Update `schema.sql` to reflect new column name, constraint, and default

## 3. Backend — Entity & Repository

- [x] 3.1 Rename `PassionLevel` type to `Hype` in `entity/artist.go`, update constants: `HypeWatch`, `HypeHome`, `HypeNearby`, `HypeAnywhere`
- [x] 3.2 Rename `FollowedArtist.PassionLevel` field to `Hype`
- [x] 3.3 Update `ArtistRepository` interface: `SetPassionLevel` → `SetHype`
- [x] 3.4 Update `artist_repo.go` queries and methods to use `hype` column name
- [x] 3.5 Add `ListFollowersWithHype` repository method that joins `followed_artists` + `users` + `homes` to return follower ID, hype, and home level_1

## 4. Backend — Use Case

- [x] 4.1 Update `ArtistUseCase` interface: `SetPassionLevel` → `SetHype`
- [x] 4.2 Update use case implementation to use new entity types and method names
- [x] 4.3 Add hype filtering logic to `NotifyNewConcerts()`: call `ListFollowersWithHype`, filter by WATCH (skip), HOME (adminArea match), ANYWHERE (send all), NEARBY (fallback to ANYWHERE)
- [x] 4.4 Update `PushNotificationUseCase` to accept concert venue adminArea for HOME filtering

## 5. Backend — RPC Adapter

- [x] 5.1 Rename `SetPassionLevel` handler to `SetHype` in `artist_handler.go`
- [x] 5.2 Update mapper: `passionLevelToProto` → `hypeToProto`, `PassionLevelFromProto` → `HypeFromProto`
- [x] 5.3 Update `FollowedArtistToProto` mapper to use `hype` field
- [x] 5.4 Update handler validation and error messages

## 6. Backend — Tests

- [x] 6.1 Update existing passion level tests to use hype naming
- [x] 6.2 Add unit tests for hype-based notification filtering (WATCH skip, HOME match/no-match/no-home, ANYWHERE send, NEARBY fallback)
- [x] 6.3 Regenerate mocks with `mockery` for updated interfaces

## 7. Frontend — Services & Data

- [x] 7.1 Update `artist-service-client.ts`: rename `passionLevel` to `hype`, update RPC call from `setPassionLevel` to `setHype`
- [x] 7.2 Update `FollowedArtistInfo` interface: `passionLevel` → `hype`
- [x] 7.3 Update `mapLocalPassionLevel` → `mapLocalHype` for onboarding local data mapping

## 8. Frontend — My Artists UI

- [x] 8.1 Rename `PASSION_LEVEL_META` to `HYPE_META` with updated keys and icons: WATCH(👀), HOME(🔥), ANYWHERE(🔥🔥🔥); omit NEARBY from selector
- [x] 8.2 Update `my-artists-page.ts`: rename all passion-related methods and properties (passionIcon → hypeIcon, openPassionSelector → openHypeSelector, selectPassionLevel → selectHype, etc.)
- [x] 8.3 Update `my-artists-page.html`: rename template bindings and labels
- [x] 8.4 Update Grid view: ANYWHERE tiles span 2x2 (previously Must Go)
- [x] 8.5 Update context menu and bottom sheet to show 3 options (WATCH, HOME, ANYWHERE)

## 9. Frontend — i18n & Onboarding

- [x] 9.1 Replace `passionLevel.*` i18n keys with `hype.*` keys in EN translation: watch="Watch", home="Home", nearby="NearBy", anywhere="Anywhere"
- [x] 9.2 Replace `passionLevel.*` i18n keys with `hype.*` keys in JA translation: watch="観測のみ", home="地元のみ", nearby="近郊まで", anywhere="遠征OK"
- [x] 9.3 Update passion explanation dialog text to describe hype and notification scope
- [x] 9.4 Update onboarding step 5 to use hype terminology and default to ANYWHERE visual demo
- [x] 9.5 Update coach mark text for hype selector
