## Why

The listening service returns many similar artists without an MBID, and ArtistUseCase.ListSimilar drops them, so well-known artists are missing from a fan's similar artists. Measured on 2026-11-28 over four artists (sumika, YOASOBI, back number, King Gnu): 51 of 200 similar results had no MBID. 14 of them were a second entry of an artist the same list already held with an MBID, and 37 were really lost. For 33 of those 37 the music catalog has an artist whose name or alias equals the result's name (9 by the name, 24 only by an alias); mostly Japanese artists listed under a romanized name.

## What Changes

- A refresh of an artist stores the catalog's name and activity status only while the artist still has the MBID they were read for. Today (backend v1.162.0) a refresh that overlaps an MBID correction writes the namesake's name and activity status over the corrected artist until the next refresh, up to 30 days later (found in review; not observed in production).
- An Artist gets known names: its name and the music catalog's aliases for it, normalized. They are stored whenever the catalog's identity of an artist is stored, and refreshed by the daily catalog read. No catalog call is added: aliases come with the artist read that already happens.
- ArtistUseCase.ListSimilar looks a result without an MBID up among the registered artists by name, and includes the artist when exactly one registered artist is known by that name and it is offered to fans. Such a result still registers nothing.
- The number of results without an MBID that were matched, matched more than one artist or matched none is logged, to decide whether a background lookup in the music catalog is worth building.

Not in this change: asking the music catalog about unmatched names (in the request or in the background), registering artists from results without an MBID, and the same matching for name search and charts.

## Capabilities

### New Capabilities

- `components/entity/artist/list-by-known-names`: Artist.ListByKnownNames, the registered artists found under given names.
- `components/entity/artist/update-known-names`: Artist.UpdateKnownNames, replaces an artist's known names.

### Modified Capabilities

- `components/entity/artist` (Purpose): attribute `known_names`, and the rule that normalizes a known name.
- `components/entity/artist/get-artist`: also returns the catalog's aliases.
- `components/entity/artist/update-name`, `components/entity/artist/update-activity-ended`: store only while the artist still has the MBID the value was read for.
- `components/entity/artist/create`: stores the artist's known names.
- `components/entity/artist/update-mbid`: replaces the known names with the given ones.
- `components/usecase/artist/list-similar` (Purpose, at archive): includes registered artists for results without an MBID.
- `components/usecase/artist/refresh`: keeps the known names in line with the catalog.
- `components/usecase/artist/verify-mbid`: stores the verified artist's known names.
- `components/usecase/artist/correct-mbid`: stores the chosen artist's known names.
- `components/usecase/artist/create`: registers with the catalog's known names.
- `components/usecase/artist/search`: registers a new match with the match's name as its only known name; VerifyMBID stores the catalog's names.
- `stories/discover-artists`: a similar artist listed without an MBID is offered when it is registered.

Entity operations used and unchanged: Artist.Get, Artist.ListSimilar, Artist.FilterArtistsByMBID, Artist.ListByMBIDs.

This change builds on change verify-artist-mbid (`mbid_status`, `listening_mbid`, ArtistUseCase.VerifyMBID): it is implemented on that backend and archived after it.

## Impact

- backend: column `artists.known_names` with a GIN index (migration with a backfill from the name); MusicBrainz artist read with `inc=aliases`; the artist repository; ArtistUseCase.
- No proto, frontend or infrastructure change; known names are not exposed by any API.
- Existing artists are found by their name at once, and by their aliases after the daily refresh has read them (every artist within 30 days).
