## 1. Frontend: Remove SearchNewConcerts from Discovery page

- [x] 1.1 In `discovery-route.ts`, remove the `await this.concertService.searchNewConcerts(artistId)` call from `searchConcertsForArtist()`
- [x] 1.2 Remove the `searchNewConcerts` method from `ConcertServiceClient` in `concert-service.ts`
- [x] 1.3 Verify `searchConcertsForArtist()` still calls `listConcerts`, `addArtistWithConcerts`, and publishes the snack notification correctly

## 2. Frontend: Tests

- [x] 2.1 Update or remove any unit tests that assert `searchNewConcerts` is called after a follow action
- [x] 2.2 Add or update tests to verify `listConcerts` is called (and `searchNewConcerts` is NOT called) after follow in `onArtistSelected`, `onFollowFromSearch`, and `loading()`
