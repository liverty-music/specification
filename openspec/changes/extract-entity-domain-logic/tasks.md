## 1. ZKP signal parsing

- [ ] 1.1 Create `entity/zkp_signals.go` with exported `ZKPPublicSignals` type (renamed from private `publicSignals`), `ParseZKPPublicSignals(proof []byte) (*ZKPPublicSignals, error)` function, `BigIntToBytes32(b *big.Int) [32]byte`, and `BytesEqual(a, b [32]byte) bool`
- [ ] 1.2 Add `func (s *ZKPPublicSignals) VerifyEventID(expectedUUID string) error` method to `entity/zkp_signals.go`
- [ ] 1.3 Write `entity/zkp_signals_test.go` -- table-driven tests for `ParseZKPPublicSignals` (valid proof, invalid JSON, missing signals), `VerifyEventID` (match, mismatch, invalid UUID), `BigIntToBytes32` (round-trip), `BytesEqual` (identical, different)
- [ ] 1.4 Update `usecase/entry_uc.go` to call `entity.ParseZKPPublicSignals()`, `entity.BigIntToBytes32()`, `entity.BytesEqual()`, and `ZKPPublicSignals.VerifyEventID()`; remove private `parsePublicSignals`, `bigIntToBytes32`, `bytesEqual`, `publicSignals` type, and `verifyEventID`

## 2. ScrapedConcert to Concert conversion

- [ ] 2.1 Add `func (sc *ScrapedConcert) ToConcert(artistID, eventID, venueID string) *Concert` method to `entity/concert.go`
- [ ] 2.2 Write tests for `ScrapedConcert.ToConcert()` in `entity/concert_test.go` -- covering full field mapping, nil optional fields, and distinct outputs for different IDs
- [ ] 2.3 Update `usecase/concert_uc.go` to call `sc.ToConcert(artistID, eventID, venueID)` instead of inline Concert construction
- [ ] 2.4 Update `usecase/concert_creation_uc.go` to call `sc.ToConcert(artistID, eventID, venueID)` instead of inline Concert construction

## 3. Parsed email data journey status

- [ ] 3.1 Add `func (p *ParsedEmailData) JourneyStatus(emailType TicketEmailType) *TicketJourneyStatus` method to the appropriate entity file (`entity/ticket_email.go` or `entity/ticket_email_parser.go`)
- [ ] 3.2 Write tests for `ParsedEmailData.JourneyStatus()` -- covering purchase confirmation, entry confirmation, refund, and unknown email type scenarios
- [ ] 3.3 Update `usecase/ticket_email_uc.go` to call `parsed.JourneyStatus(emailType)` instead of private `mapParsedToJourneyStatus()`; remove the private function

## 4. SearchLog freshness and pending checks

- [ ] 4.1 Add `func (sl *SearchLog) IsFresh(now time.Time, ttl time.Duration) bool` method to `entity/search_log.go`
- [ ] 4.2 Add `func (sl *SearchLog) IsPending(now time.Time, timeout time.Duration) bool` method to `entity/search_log.go`
- [ ] 4.3 Write `entity/search_log_test.go` -- table-driven tests for `IsFresh` (fresh, stale, non-completed) and `IsPending` (active, timed-out, completed)
- [ ] 4.4 Update `usecase/concert_uc.go` to call `searchLog.IsFresh()` and `searchLog.IsPending()` instead of inline time comparison logic

## 5. Push notification payload

- [ ] 5.1 Add `NotificationPayload` struct and `NewConcertNotificationPayload(artist *Artist, concertCount int) *NotificationPayload` to `entity/push_notification.go`
- [ ] 5.2 Write tests for `NewConcertNotificationPayload()` in `entity/push_notification_test.go` -- covering single concert, multiple concerts, and artist ID in payload data
- [ ] 5.3 Update `usecase/push_notification_uc.go` to call `entity.NewConcertNotificationPayload()` instead of inline payload construction; remove private payload struct and builder

## 6. Usecase cleanup and verification

- [ ] 6.1 Run `make check` to verify all lint and tests pass
- [ ] 6.2 Run `mockery` if any interface signatures changed (not expected for this change)
