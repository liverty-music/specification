## MODIFIED Requirements

### Requirement: Search returns the catalog's matches as registered artists
ArtistUseCase.Search SHALL look the query up with Artist.Search, reduce the matches with Artist.FilterArtistsByMBID, find the ones already registered with Artist.ListByMBIDs (under their mbid or listening_mbid), and register the rest with Artist.Create with the match's MBID as both its listening MBID and its MBID and mbid_status Unverified, without reading the music catalog: Artist.Create announces each new artist, and the announcement runs ArtistUseCase.VerifyMBID for it. Search SHALL return one registered artist per match in the catalog's order, listing an artist once when several matches resolve to it, and only the artists offered to fans (Verified, activity not ended), so a match registered by this call is not returned until it is Verified.

#### Scenario: Known and new matches
- **WHEN** the catalog matches a registered Verified artist and an unregistered artist, in that order
- **THEN** Search registers only the unregistered one, Unverified and without reading the catalog, and returns only the registered Verified artist

#### Scenario: Match without MBID
- **WHEN** the catalog matches an artist without an MBID
- **THEN** that match is neither registered nor returned

#### Scenario: No match with an MBID
- **WHEN** no catalog match has an MBID
- **THEN** Search fails with NotFound and registers nothing

#### Scenario: Match under a replaced MBID
- **WHEN** the catalog matches MBID A and a registered artist has listening_mbid A and mbid B
- **THEN** Search returns that artist and registers nothing

#### Scenario: Two matches of one artist
- **WHEN** the catalog matches MBIDs A and B of one registered artist
- **THEN** Search returns that artist once

#### Scenario: Registered artist not yet verified
- **WHEN** the catalog matches a registered artist whose mbid_status is Unverified
- **THEN** Search does not return it and does not verify it

#### Scenario: Ended artist
- **WHEN** the catalog matches a registered Verified artist whose activity_ended is true
- **THEN** Search does not return it

### Requirement: Search reuses a recent result
ArtistUseCase.Search SHALL return the earlier result, without consulting the catalog or registering anything, when the same query was answered within the last 6 hours, including the matches it registered Unverified and did not return, and leaving out the artists not offered to fans at the time of this call: it SHALL read the current mbid_status and activity_ended of the earlier result's artists with one Artist.ListByMBIDs call.

#### Scenario: Repeated query
- **WHEN** Search is called twice with the same query 10 minutes apart
- **THEN** the second call returns the first call's result without a catalog lookup

#### Scenario: Result older than 6 hours
- **WHEN** Search is called with the same query more than 6 hours after the last such call
- **THEN** the catalog is consulted again

#### Scenario: Match registered by the earlier call and Verified since
- **WHEN** Search registered a new match Unverified 1 hour ago, and its announcement has made it Verified since
- **THEN** a second call with the same query returns it, without a catalog lookup

#### Scenario: Artist marked ended after the result was reused
- **WHEN** Search answered a query 1 hour ago, and an artist in that answer has had activity_ended true since then
- **THEN** a second call with the same query returns the earlier result without that artist and without a catalog lookup

### Requirement: Search reports failures
ArtistUseCase.Search SHALL return the errors of Artist.Search, Artist.ListByMBIDs, and Artist.Create unchanged, preserving each port's failure code rather than replacing it with Internal. 

#### Scenario: Catalog unavailable
- **WHEN** Artist.Search fails with Unavailable
- **THEN** Search fails with Unavailable

#### Scenario: Catalog rate-limited
- **WHEN** Artist.Search fails with ResourceExhausted
- **THEN** Search fails with ResourceExhausted

#### Scenario: Catalog request timed out
- **WHEN** Artist.Search fails with DeadlineExceeded
- **THEN** Search fails with DeadlineExceeded
