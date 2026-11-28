## Why

For a shared name, the music catalog lookup used by artist search can return a namesake's MBID, and Artist keeps whatever MBID it was registered with. The daily catalog refresh then overwrites the artist's name and `activity_ended` from the namesake, and the official-site refresh reads the namesake's links. Penthouse was left out of concert discovery for a day because the namesake band had ended in 2002 (backend#920). Nothing can change an MBID, and Last.fm keeps returning the wrong one, so correcting a row by hand lets the next search register a second row under the wrong MBID.

## What Changes

- An artist remembers the MBIDs it was corrected from (`other_mbids`); a search that returns one of them finds the corrected artist and registers nothing.
- New `Artist.UpdateMBID` replaces an artist's MBID, keeps the replaced one, and clears everything read from the namesake (images, official site, check time, `activity_ended`).
- New `ArtistUseCase.CorrectMBID` checks that the catalog knows the new MBID, stores it, and reads the artist again from the catalog so the name and `activity_ended` follow the right person. An admin runs it as a command of the workflow worker (`worker artist correct-mbid <artist id> <mbid>`), with a runbook.
- `Artist.ListByMBIDs`, `Artist.Create` and `ArtistUseCase.Search` resolve a remembered MBID to its artist.
- Every registered artist is checked once for a namesake, and the wrong ones found are corrected with the new command (an operational task, recorded in the tasks).

## Capabilities

### New Capabilities

- `components/entity/artist/update-mbid`: replace an artist's MBID, remember the old one, clear what came from the namesake.
- `components/usecase/artist/correct-mbid`: the admin correction of an artist's MBID.

### Modified Capabilities

- `components/entity/artist` (Purpose): the attribute table gains `other_mbids`; a delta adds the rule that one MBID names one artist.
- `components/entity/artist/list-by-mbids`: finds an artist under any MBID it has had, once per artist.
- `components/entity/artist/create`: an MBID an artist was corrected from counts as registered.
- `components/usecase/artist/search`: returns one registered artist per match, finding the corrected artist under a replaced MBID. It relies on the modified `Artist.ListByMBIDs` and `Artist.Create`; `Artist.FilterArtistsByMBID` is unchanged.

## Impact

- backend: `artists.other_mbids` column and migration, `entity.Artist`, `ArtistRepository` (`UpdateMBID`, `ListByMBIDs`, `Create`), `ArtistUseCase` (`CorrectMBID`, `persistArtists` shared by Search, ListSimilar and ListTop), a `worker artist` command and its DI.
- cloud-provisioning: a runbook only (`docs/runbooks/correct-artist-mbid.md`).
- No proto, frontend or infrastructure change; no new RPC.
- Production: the migration applies on merge (`backend-migrations` tracks `main`); correcting the wrong artists is a break-glass write the owner approves.
