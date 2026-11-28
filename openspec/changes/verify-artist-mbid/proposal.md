## Why

Artists are registered with the MBID the listening service (where name search, charts and similar artists come from) returns, and that MBID sometimes names a namesake in the music catalog: on 2026-11-26 Ado, Aimer, Yama, Sumika, Saji and Penthouse carried a namesake's MBID, and Penthouse dropped out of concert search because the namesake's activity had ended (liverty-music/backend#920). Change correct-artist-mbid made a correction possible, but a correction cannot simply replace the MBID: the listening service still files the artist under the namesake's MBID, and for sumika it answers similar-artist lookups only under that MBID. Fans are also still offered artists that concert search never searches (activity ended) and artists whose MBID nobody has checked.

## What Changes

- An Artist keeps two MBIDs: `mbid`, the artist's own identity in the music catalog, and `listening_mbid`, the MBID the listening service files it under. Results of name search, charts and similar artists are matched by either; similar artists are looked up by `listening_mbid`. **BREAKING** (data): `other_mbids` is replaced by `listening_mbid`; it holds no value in production.
- An Artist gets `mbid_status`: Unverified, Verified or Ambiguous.
- A new usecase, ArtistUseCase.VerifyMBID, checks an Unverified artist's MBID against the catalog's other artists of the same name: with no namesake it is Verified; with namesakes, it is corrected to the one namesake that has an official homepage when exactly one has; otherwise it becomes Ambiguous and an error is logged so the owner is alerted. It runs when an artist is registered and daily for every artist still Unverified.
- ArtistUseCase.Search verifies the MBIDs of the matches it registers before it answers, so a first search returns a verified artist.
- ArtistUseCase.Search, ListTop and ListSimilar return only artists whose `mbid_status` is Verified and whose activity has not ended, also when they reuse an earlier result. **BREAKING** (behavior): a name search no longer returns an artist whose activity has ended.
- The admin console gets an Artist MBIDs screen: it lists the Ambiguous artists with the catalog's namesakes of each (country, life span, disambiguation, official homepage) and lets an admin choose the right MBID, through new admin RPCs and ArtistUseCase.CorrectMBID, which now also marks the artist Verified.
- **BREAKING** (operations): the command `worker artist correct-mbid` and its runbook are removed; the admin console replaces them.
- The Last.fm client's doc comment is corrected to the current Last.fm API Terms of Service (no published numeric rate limit; storage under local law; non-commercial use only, tracked in liverty-music/backend#953). The client keeps its throttle of 5 requests per second.

Not in this change: a listener-count floor (a namesake's MBID comes with the right artist's listener count, so a floor cannot catch it, and concert search does not skip artists by listener count); followed artists whose activity ended stay in My Artists; reducing registrations nobody uses.

## Capabilities

### New Capabilities

- `components/entity/catalog-artist`: an artist as the music catalog records it, offered as a namesake candidate (MBID, name, country, life span, disambiguation, official homepage).
- `components/entity/artist/list-namesakes`: Artist.ListNamesakes, the catalog's artists whose name equals a given name.
- `components/entity/artist/mark-mbid-ambiguous`: Artist.MarkMBIDAmbiguous, records that an artist's MBID could not be verified.
- `components/entity/artist/list-by-mbid-status`: Artist.ListByMBIDStatus, the registered artists in one `mbid_status`.
- `components/usecase/artist/verify-mbid`: ArtistUseCase.VerifyMBID, the check of an Unverified artist's MBID, its triggers and its alert.
- `components/usecase/artist/list-namesakes`: ArtistUseCase.ListNamesakes, an artist's namesake candidates with their official homepages, for the admin console.
- `components/usecase/artist/list-by-mbid-status`: ArtistUseCase.ListByMBIDStatus, for the admin console.
- `components/infrastructure/admin/web/route/artist-mbids`: the admin console's Artist MBIDs screen.

### Modified Capabilities

- `components/entity/artist` (Purpose): attributes `listening_mbid` and `mbid_status` replace `other_mbids`; requirements "One MBID names one artist" and "A new artist starts without images" change.
- `components/entity/artist/create`: a registration matches `mbid` or `listening_mbid`, sets `listening_mbid`, and takes the artist's `mbid_status`.
- `components/entity/artist/list-by-mbids`: matches `mbid` or `listening_mbid`.
- `components/entity/artist/update-mbid`: keeps `listening_mbid`, marks the artist Verified, no longer keeps replaced MBIDs.
- `components/entity/artist/list-similar` (Purpose): looks the artist up by its `listening_mbid`; the Purpose names the listening service.
- `components/usecase/artist/search` (Purpose, at archive): verifies new matches before registering them; returns only Verified artists whose activity has not ended, also from a reused result.
- `components/usecase/artist/list-top` (Purpose, at archive): returns only Verified artists whose activity has not ended.
- `components/usecase/artist/list-similar` (Purpose, at archive): the same, and the seed is looked up by its `listening_mbid`.
- `components/usecase/artist/refresh`: no longer runs on registration (VerifyMBID does); the daily run is unchanged.
- `components/usecase/artist/correct-mbid`: marks the artist Verified; reached from the admin console.
- `components/usecase/artist/create`: an artist an admin registers with its MBID is Verified.
- `components/adapter/admin/api/rpc/artist`: ListByMbidStatus, ListNamesakes and CorrectMbid.
- `stories/discover-artists` (Purpose): only Verified artists whose activity has not ended are offered, by every discovery path; a discovered artist's MBID is verified.

Entity operations used and unchanged: Artist.Get, Artist.GetArtist, Artist.ListOfficialSiteRelations, Artist.SelectOfficialSite, Artist.UpdateName, Artist.UpdateActivityEnded, Artist.FilterArtistsByMBID, Artist.Search, Artist.ListTop.

## Impact

- specification: `entity/v1` gains `CatalogArtist` and `ArtistMbidStatus`; the admin `ArtistService` gains ListByMbidStatus, ListNamesakes and CorrectMbid; a proto release.
- backend: `artists` columns `listening_mbid` and `mbid_status` replace `other_mbids` (migration with backfill, Penthouse's `listening_mbid` set to the MBID the listening service returns for it); MusicBrainz name search; ArtistUseCase changes; the event consumer `refresh-artist` runs VerifyMBID; the daily job verifies Unverified artists; the admin RPC handlers; the `worker artist correct-mbid` command removed; Last.fm client doc comment.
- frontend: the admin console's Artist MBIDs screen and its navigation entry.
- cloud-provisioning: the runbook `docs/runbooks/correct-artist-mbid.md` removed.
- Production: after the migration every registered artist is Unverified and hidden from discovery until the daily job verifies it (about 5,500 artists at the catalog's 1 request per second); the six artists of liverty-music/backend#920 are fixed on the new screen.
