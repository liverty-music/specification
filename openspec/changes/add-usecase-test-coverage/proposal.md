## Why

Two usecase files -- `ticket_email_uc.go` and `artist_image_sync_uc.go` -- currently have zero unit test coverage. Every other usecase file in the project has corresponding `_test.go` files. This gap means regressions in ticket email creation/update orchestration and artist image sync logic can ship undetected. Adding tests now is especially important because the parallel `extract-entity-domain-logic` change is moving `mapParsedToJourneyStatus` to the entity layer, and the usecase methods that call it need their own coverage to validate the integration seam.

## What Changes

- **Add `ticket_email_uc_test.go`**: Table-driven unit tests covering `Create()`, `Update()`, `buildNewTicketEmail()`, and `determineJourneyStatus()` methods. Mock all repository, parser, and journey dependencies using existing mockery-generated mocks.
- **Add `artist_image_sync_uc_test.go`**: Table-driven unit tests covering `SyncArtistImage()` and `profileLogoColor()` methods. Mock artist repository, image resolver, and logo image fetcher dependencies.

## Capabilities

### New Capabilities

- `usecase-test-coverage`: Defines minimum test scenario requirements for usecase-layer unit tests on `TicketEmailUsecase` and `ArtistImageSyncUsecase`.

### Modified Capabilities

(none)

## Impact

- **`internal/usecase/`**: Two new `_test.go` files added. No production code changes.
- **No API changes**: No proto, RPC, or database changes.
- **No migration needed**: No schema or infrastructure impact.
- **CI**: Test count increases; no new dependencies required (testify and mockery already in use).
