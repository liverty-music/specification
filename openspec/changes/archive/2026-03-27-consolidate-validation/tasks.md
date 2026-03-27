## 1. Entity Layer

- [x] 1.1 Add `entity.ValidateEthereumAddress(addr string) error` with `^0x[0-9a-fA-F]{40}$` regex and tests per spec scenarios
- [x] 1.2 Remove `ethAddressRe` from `ticket_uc.go` and update `validateMintParams` to call `entity.ValidateEthereumAddress`

## 2. Mapper Helper

- [x] 2.1 Add `mapper.GetExternalUserID(ctx) (string, error)` that extracts `claims.Sub` with `Unauthenticated` error on missing/empty (D3)
- [x] 2.2 Add tests for `GetExternalUserID`: missing claims, nil claims, empty Sub, valid Sub

## 3. Follow/Concert Identity Unification (No DB Migration Needed)

- [x] 3.1 ~~Generate Atlas migration~~ — DB already uses internal `user_id` UUID in `followed_artists` table. No migration needed.
- [x] 3.2 ~~Update follow repository queries~~ — Repository already uses internal UUIDs. No change needed.
- [x] 3.3 ~~Update concert repository queries~~ — Repository already uses internal UUIDs. No change needed.
- [x] 3.4 ~~Update kustomization.yaml~~ — No migration file to add.
- [x] 3.5 Remove `resolveUserID` calls from `follow_uc.go` — usecase will receive internal UUID directly from handler
- [x] 3.6 Remove `resolveUserID` / `GetByExternalID` calls from `concert_uc.go` — `ListByFollower` receives internal UUID; `ListByFollowerGrouped` receives internal UUID + `*entity.Home`
- [x] 3.7 Remove `userRepo` dependency from `followUseCase` struct (only used for `resolveUserID`)
- [x] 3.8 Update `concert_uc.ListByFollowerGrouped` signature to accept `(ctx, userID string, home *entity.Home)` instead of external ID
- [x] 3.9 Remove `usecase/auth.go` (`resolveUserID`) if no longer referenced
- [x] 3.10 Update DI wiring in `internal/di/` to remove `userRepo` from `NewFollowUseCase`

## 4. Handler Validation Removal

- [x] 4.1 `user_handler.go`: Remove nil/empty checks (req nil, home nil). Keep mapper calls and usecase delegation only
- [x] 4.2 `artist_handler.go`: Remove nil checks on name, artist_id, url fields
- [x] 4.3 `follow_handler.go`: Remove artist_id nil checks. Remove hype enum `ok` guard (keep mapping). Switch from `claims.Sub` to `GetExternalUserID` → `GetByExternalID` → `user.ID`
- [x] 4.4 `ticket_handler.go`: Remove req nil, event_id nil, ticket_id nil checks
- [x] 4.5 `ticket_journey_handler.go`: Remove event_id nil checks and status enum `ok` guard
- [x] 4.6 `ticket_email_handler.go`: Remove email_type enum `ok` guard, event_ids element nil check, ticket_email_id nil check
- [x] 4.7 `entry_handler.go`: Remove req nil, event_id nil/empty, proof_json empty, public_signals_json empty checks
- [x] 4.8 `push_notification_handler.go`: Remove endpoint/p256dh/auth empty string checks
- [x] 4.9 `concert_handler.go`: Remove artist_id empty check. Switch `ListByFollower`/`ListByFollowerGrouped` from `claims.Sub` to `GetExternalUserID` → `GetByExternalID` → `user.ID`

## 5. Usecase Validation Removal

- [x] 5.1 `user_uc.go`: Remove `id == ""` and `home == nil` guards. Keep `home.Validate()` call
- [x] 5.2 `artist_uc.go`: Remove MBID, Name, URL, artistID, query empty checks
- [x] 5.3 `follow_uc.go`: Remove all `userID == "" || artistID == ""` guards. Update method signatures if parameter type changes
- [x] 5.4 `concert_uc.go`: Remove artistID, externalUserID, artistIDs empty checks. Rename `externalUserID` params to `userID`
- [x] 5.5 `ticket_uc.go`: Remove `validateMintParams` nil/empty guards except `entity.ValidateEthereumAddress` call. Remove `GetTicket` and `ListTicketsForUser` empty guards
- [x] 5.6 `entry_uc.go`: Remove params nil, eventID/proofJSON/publicSignalsJSON empty guards. Remove `GetMerklePath`/`BuildMerkleTree` empty guards
- [x] 5.7 `ticket_journey_uc.go`: Remove userID, eventID, status guards
- [x] 5.8 `ticket_email_uc.go`: Remove userID, eventIDs, emailType, rawBody, ticketEmailID guards
- [x] 5.9 `push_notification_uc.go`: Verify no guards to remove (confirmed none exist)

## 6. Test Updates

- [x] 6.1 Remove handler test cases that assert `InvalidArgument` for nil/empty/invalid-enum inputs (interceptor covers these)
- [x] 6.2 Remove usecase test cases that assert `InvalidArgument` for empty parameter guards
- [x] 6.3 Update follow/concert handler tests to mock `GetByExternalID` call (new dependency)
- [x] 6.4 Update follow/concert usecase tests: change `userID` fixture values from external IDs to internal UUIDs
- [x] 6.5 Update follow/concert repository tests: queries now use `user_id` column
- [x] 6.6 Regenerate mocks if usecase/repository interfaces changed (`mockery`)

## 7. Verification

- [x] 7.1 Run `make check` (lint + test) to verify all changes pass
- [x] 7.2 Run integration tests with local DB to verify follow/concert migration
