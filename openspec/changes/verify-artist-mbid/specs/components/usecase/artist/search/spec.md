## MODIFIED Requirements

### Requirement: Search returns the catalog's matches as registered artists
ArtistUseCase.Search SHALL look the query up with Artist.Search, reduce the matches with Artist.FilterArtistsByMBID, and find the ones already registered with Artist.ListByMBIDs (under their mbid or listening_mbid). For each remaining match it SHALL decide the match's MBID as ArtistUseCase.VerifyMBID decides it, before registering anything, and register the match with Artist.Create with the match's MBID as its listening MBID, the decided MBID, and mbid_status Verified or Ambiguous; a Verified match is registered with the catalog's name and activity status for the decided MBID, read with Artist.GetArtist as part of the decision. An Ambiguous result is logged as an error as VerifyMBID logs it. A match whose decision fails SHALL be registered Unverified with its own MBID, and Search SHALL not fail for it. Search SHALL return one registered artist per match in the catalog's order, listing an artist once when several matches resolve to it, and only the artists offered to fans (Verified, activity not ended).

#### Scenario: Known and new matches
- **WHEN** the catalog matches a registered Verified artist and an unregistered artist with no namesake, in that order
- **THEN** Search registers only the unregistered one, Verified, and returns both registered artists in that order

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

#### Scenario: New match whose MBID names a namesake
- **WHEN** an unregistered match has MBID A, which names a namesake without an official homepage, and the only other artist of the name, B, has one
- **THEN** the match is registered with listening_mbid A, mbid B and mbid_status Verified, and returned

#### Scenario: New match that is ambiguous
- **WHEN** an unregistered match's name has two catalog artists and neither has an official homepage
- **THEN** the match is registered Ambiguous, an error is logged, and it is not returned

#### Scenario: Verification unavailable
- **WHEN** Artist.ListNamesakes fails with Unavailable for an unregistered match
- **THEN** the match is registered Unverified, it is not returned, and Search returns the other matches

#### Scenario: Registered artist not yet verified
- **WHEN** the catalog matches a registered artist whose mbid_status is Unverified
- **THEN** Search does not return it and does not verify it

#### Scenario: Ended artist
- **WHEN** the catalog matches a registered Verified artist whose activity_ended is true
- **THEN** Search does not return it

### Requirement: Search reuses a recent result
ArtistUseCase.Search SHALL return the earlier result, without consulting the catalog or registering anything, when the same query was answered within the last 6 hours, leaving out the artists no longer offered to fans at the time of this call: it SHALL read the current mbid_status and activity_ended of the earlier result's artists with one Artist.ListByMBIDs call.

#### Scenario: Repeated query
- **WHEN** Search is called twice with the same query 10 minutes apart
- **THEN** the second call returns the first call's result without a catalog lookup

#### Scenario: Result older than 6 hours
- **WHEN** Search is called with the same query more than 6 hours after the last such call
- **THEN** the catalog is consulted again

#### Scenario: Artist marked ended after the result was reused
- **WHEN** Search answered a query 1 hour ago, and an artist in that answer has had activity_ended true since then
- **THEN** a second call with the same query returns the earlier result without that artist and without a catalog lookup

### Requirement: Search reports failures
ArtistUseCase.Search SHALL return the errors of Artist.Search, Artist.ListByMBIDs, and Artist.Create unchanged, preserving each port's failure code rather than replacing it with Internal. A failure of the MBID decision for a match is not a failure of Search.

#### Scenario: Catalog unavailable
- **WHEN** Artist.Search fails with Unavailable
- **THEN** Search fails with Unavailable

#### Scenario: Catalog rate-limited
- **WHEN** Artist.Search fails with ResourceExhausted
- **THEN** Search fails with ResourceExhausted

#### Scenario: Catalog request timed out
- **WHEN** Artist.Search fails with DeadlineExceeded
- **THEN** Search fails with DeadlineExceeded
