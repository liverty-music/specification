## 1. Entity validation & enum methods

- [x] 1.1 Add `Home.Validate() error` method to `entity/user.go` with ISO 3166 regex validation; move `countryCodeRe` and `iso31662Re` from `usecase/user_uc.go`
- [x] 1.2 Add `Hype.IsValid() bool` method to `entity/follow.go`
- [x] 1.3 Write `entity/user_test.go` — table-driven tests for `Home.Validate()` covering all 7 scenarios from spec
- [x] 1.4 Write `entity/follow_test.go` — table-driven tests for `Hype.IsValid()` covering known and unknown values

## 2. Notification eligibility logic

- [x] 2.1 Add `Hype.ShouldNotify(home *Home, venueAreas map[string]struct{}, concerts []*Concert) bool` method to `entity/follow.go`
- [x] 2.2 Write tests for `Hype.ShouldNotify()` in `entity/follow_test.go` covering all 10 scenarios from spec (HypeWatch, HypeHome match/no-match/nil-home/empty-Level1, HypeNearby nearby/distant/nil-home, HypeAway, unknown)
- [x] 2.3 Update `usecase/push_notification_uc.go` to call `f.Hype.ShouldNotify()` instead of inline switch; remove `hasNearbyConcert()` private function

## 3. Concert grouping & deduplication

- [x] 3.1 Add `GroupByDateAndProximity(concerts []*Concert, home *Home) []*ProximityGroup` to `entity/concert.go`; move from `usecase/concert_uc.go`
- [x] 3.2 Add `ScrapedConcert.DedupeKey() string` and `ScrapedConcert.DateVenueKey() string` methods to `entity/concert.go`; remove `concertKey()` and `dateVenueKey()` from `usecase/concert_uc.go`
- [x] 3.3 Write `entity/concert_test.go` — table-driven tests for `Concert.ProximityTo()` covering all 9 scenarios from spec (nil home, nil venue, admin match, nearby, distant, no venue coords, no home centroid, admin priority, nil admin area)
- [x] 3.4 Write tests for `GroupByDateAndProximity()` in `entity/concert_test.go` covering all 4 scenarios (empty, single date mixed, multiple dates order, nil home)
- [x] 3.5 Write tests for `ScrapedConcert.DedupeKey()` and `DateVenueKey()` in `entity/concert_test.go` covering all 3 scenarios
- [x] 3.6 Update `usecase/concert_uc.go` to call entity-level `GroupByDateAndProximity()`, `DedupeKey()`, and `DateVenueKey()`; remove private functions

## 4. Artist filtering

- [x] 4.1 Add `FilterArtistsByMBID(artists []*Artist) []*Artist` to `entity/artist.go`; move from `usecase/artist_uc.go`
- [x] 4.2 Write `entity/artist_test.go` — table-driven tests for `FilterArtistsByMBID()` covering all 4 scenarios (mixed, all empty, no duplicates, empty input)
- [x] 4.3 Update `usecase/artist_uc.go` to call `entity.FilterArtistsByMBID()` instead of private `filterAndDedupByMBID()`

## 5. Entity constructors

- [x] 5.1 Add `NewOfficialSite(artistID, url string) *OfficialSite` constructor to `entity/artist.go`
- [x] 5.2 Add `NewVenueFromScraped(name string) *Venue` constructor to `entity/venue.go`
- [x] 5.3 Add `GenerateTokenID() (uint64, error)` to `entity/ticket.go`; move from `usecase/ticket_uc.go`
- [x] 5.4 Write tests for `NewOfficialSite()` in `entity/artist_test.go` (ID generation, unique IDs, field mapping)
- [x] 5.5 Write tests for `NewVenueFromScraped()` in `entity/venue_test.go` (ID generation, defaults)
- [x] 5.6 Write tests for `GenerateTokenID()` in `entity/ticket_test.go` (non-zero, monotonic ordering)
- [x] 5.7 Update `usecase/follow_uc.go` to use `entity.NewOfficialSite()` instead of inline construction
- [x] 5.8 Update `usecase/ticket_uc.go` to use `entity.GenerateTokenID()` instead of private `generateTokenID()`

## 6. Usecase cleanup & integration

- [x] 6.1 Update `usecase/user_uc.go` to call `home.Validate()` instead of private `validateHome()`; remove `validateHome()`, `countryCodeRe`, `iso31662Re`
- [x] 6.2 Run `make check` to verify all lint and tests pass
- [x] 6.3 Run `mockery` if any interface signatures changed
