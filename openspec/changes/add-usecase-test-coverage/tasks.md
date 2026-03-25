## 1. Verify Mock Availability

- [ ] 1.1 Confirm mockery-generated mocks exist for `TicketEmailRepository`, `TicketEmailParser`, `TicketJourneyRepository`; generate any missing mocks with `mockery`
- [ ] 1.2 Confirm mockery-generated mocks exist for `ArtistRepository`, `ArtistImageResolver`, `LogoImageFetcher`; generate any missing mocks with `mockery`

## 2. TicketEmailUsecase Tests (HIGH priority)

- [ ] 2.1 Create `internal/usecase/ticket_email_uc_test.go` with test scaffold and helper functions for building test fixtures (mock parser responses, sample TicketEmail entities)
- [ ] 2.2 Add table-driven tests for `Create()`: valid lottery info, valid lottery result, invalid emailType, empty rawBody, parser error, repository error
- [ ] 2.3 Add table-driven tests for `Update()`: valid update, non-existent ID, wrong userID ownership check, journey status upsert triggered
- [ ] 2.4 Add tests for `buildNewTicketEmail()`: verify timestamp parsing and field mapping from parsed data
- [ ] 2.5 Add tests for `determineJourneyStatus()`: valid mapping returns correct status, no mapping returns default

## 3. ArtistImageSyncUsecase Tests (MEDIUM priority)

- [ ] 3.1 Create `internal/usecase/artist_image_sync_uc_test.go` with test scaffold and helper functions for building test fixtures (sample Artist entities, mock image responses)
- [ ] 3.2 Add table-driven tests for `SyncArtistImage()`: valid MBID full flow, empty MBID early return, image resolver NotFound, logo fetch failure, artist repository error
- [ ] 3.3 Add tests for `profileLogoColor()`: successful download and color analysis, download failure returns nil

## 4. Validation

- [ ] 4.1 Run `go test ./internal/usecase/...` and verify all new tests pass
- [ ] 4.2 Run `make check` to confirm linting and full test suite pass
