## Why

The listening service returns many similar artists without an MBID, and ArtistUseCase.ListSimilar drops them, so well-known artists are missing from a fan's similar artists. Measured on 2026-11-28 over four artists (sumika, YOASOBI, back number, King Gnu): 51 of 200 similar results had no MBID. 14 of them were a second entry of an artist the same list already held with an MBID, and 37 were really lost. For 33 of those 37 the music catalog has an artist whose name or alias equals the result's name (9 by the name, 24 only by an alias); mostly Japanese artists listed under a romanized name.

## What Changes

- An Artist gets name keys: its name and the music catalog's aliases for it, normalized. They are stored whenever the catalog's identity of an artist is stored, and refreshed by the daily catalog read. No catalog call is added: aliases come with the artist read that already happens.
- ArtistUseCase.ListSimilar looks a result without an MBID up among the registered artists by name, and includes the artist when exactly one registered artist has that name key and it is offered to fans. Such a result still registers nothing.
- The number of results without an MBID that were matched, matched more than one artist or matched none is logged, to decide whether a background lookup in the music catalog is worth building.

Not in this change: asking the music catalog about unmatched names (in the request or in the background), registering artists from results without an MBID, and the same matching for name search and charts.

## Capabilities

### New Capabilities

- `components/entity/artist/list-by-name-keys`: Artist.ListByNameKeys, the registered artists found under given names.
- `components/entity/artist/update-name-keys`: Artist.UpdateNameKeys, replaces an artist's name keys.

### Modified Capabilities

- `components/entity/artist` (Purpose): attribute `name_keys`, and the rule that derives a name key.
- `components/entity/artist/get-artist`: also returns the catalog's aliases.
- `components/entity/artist/create`: stores the artist's name keys.
- `components/entity/artist/update-mbid`: replaces the name keys with the given ones.
- `components/usecase/artist/list-similar` (Purpose, at archive): includes registered artists for results without an MBID.
- `components/usecase/artist/refresh`: keeps the name keys in line with the catalog.
- `components/usecase/artist/verify-mbid`: stores the verified artist's name keys.
- `components/usecase/artist/correct-mbid`: stores the chosen artist's name keys.
- `components/usecase/artist/create`: registers with the catalog's name keys.
- `components/usecase/artist/search`: registers a verified match with the catalog's name keys.
- `stories/discover-artists`: a similar artist listed without an MBID is offered when it is registered.

Entity operations used and unchanged: Artist.Get, Artist.ListSimilar, Artist.FilterArtistsByMBID, Artist.ListByMBIDs, Artist.UpdateName, Artist.UpdateActivityEnded.

This change builds on change verify-artist-mbid (`mbid_status`, `listening_mbid`, ArtistUseCase.VerifyMBID): it is implemented on that backend and archived after it.

## Impact

- backend: column `artists.name_keys` with a GIN index (migration with a backfill from the name); MusicBrainz artist read with `inc=aliases`; the artist repository; ArtistUseCase.
- No proto, frontend or infrastructure change; name keys are not exposed by any API.
- Existing artists are found by their name at once, and by their aliases after the daily refresh has read them (every artist within 30 days).
