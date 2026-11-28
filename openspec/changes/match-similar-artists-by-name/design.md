## Context

See proposal.md - Why. On backend v1.162.0 (`internal/usecase/artist_uc.go`), `ListSimilar` calls Last.fm `artist.getsimilar`, drops entries without an MBID (`entity.FilterArtistsByMBID`) and registers the rest. `artists.name` holds MusicBrainz's name (often Japanese), while Last.fm lists many Japanese artists under a romanized name, so matching on `name` alone recovers about a quarter of the lost results (9 of 37 measured) and aliases most of the rest (24 of 37). The MusicBrainz client reads an artist with `GET /ws/2/artist/{mbid}?fmt=json` (`musicbrainz/client.go`, `GetArtist`), whose callers are VerifyMBID, Search, Create, CorrectMBID and Refresh. The `artists` table has 5,505 rows (2026-11-28).

## Goals / Non-Goals

**Goals:**
- Recover registered artists among the results without an MBID with one database query per ListSimilar and no added call to an external service.
- Collect the numbers that decide whether a background catalog lookup (stage 2) is needed.

**Non-Goals:**
- Fuzzy or partial name matching.
- A fallback that asks `artist.getsimilar` by name when the lookup by `listening_mbid` fails. On 2026-11-28 the lookup failed for 0 of 116 MBIDs Last.fm itself had returned, and this change registers no artist under any other MBID.

## Decisions

### D1. One array column with a GIN index

`artists.known_names TEXT[] NOT NULL`, holding the artist's known names, with `CREATE INDEX idx_artists_known_names ON artists USING gin (known_names)`. `ListByKnownNames` is one query, `WHERE known_names && $1`; `&&` (overlap) is one of the operators the built-in `array_ops` GIN operator class indexes, and GIN is meant for searching element values inside composite values (https://www.postgresql.org/docs/17/gin.html). The planner may still choose a sequential scan at the current size.

Alternative rejected: a table `artist_names (artist_id, name)` with a B-tree. It looks up as fast, but adds a table whose rows must be added and removed with every name change.

Alternative rejected: keep the raw aliases in a second column. Nothing reads an alias except the match.

The cost of GIN is slower writes; artist rows are written on registration, verification, correction and the daily refresh of one thirtieth of them.

### D2. Normalized names

NFKC normalization (`golang.org/x/text/unicode/norm`), `strings.ToLower`, surrounding white space removed and inner runs collapsed to one space. One entity function derives it for writes and lookups. The migration backfills `known_names` from `name` with `lower(regexp_replace(btrim(normalize(name, NFKC)), '\s+', ' ', 'g'))`.

### D3. Aliases arrive with the existing artist read

`GetArtist` adds `inc=aliases` and returns every alias name; `entity.Artist` carries the derived `KnownNames`. `UpdateMBID` takes the known names and writes them in its single statement. `Refresh` calls the new `UpdateKnownNames` after `UpdateName`, also when the name did not change, since aliases change on their own. `UpdateKnownNames`, `UpdateName` and `UpdateActivityEnded` write only `WHERE id = $1 AND mbid = $2`, as `UpdateFanart` does (change verify-artist-mbid), because a refresh can read an MBID that `CorrectMBID` replaces before the write; a row left unmatched is told apart from a missing artist, which stays NotFound. `Refresh` is their only caller (`artist_uc.go`). Alternative rejected: one operation writing all three, which would remove two operations other changes' specs name for a fix two conditions solve. When `GetArtist` returns another canonical MBID or fails, the writers keep their current rules; known names are only taken from a successful read.

Alternative rejected: have `UpdateName` take the known names. The name and the aliases change independently, and `Refresh` skips `UpdateName` when the name is equal.

### D4. Matching in ListSimilar

After the MBID results are registered, one `ListByKnownNames` call takes the names of every result without an MBID. A result is matched when exactly one returned artist is known by its name; that artist takes the result's position in the list, once, and is left out when it is the seed. Offered-to-fans filtering and the 6-hour cache apply to it like to any other artist. All registered artists count toward "exactly one", offered or not, so an unoffered namesake does not make the offered one look unique. No lock is needed: nothing is written from a match.

The usecase logs at INFO `similar artists without MBID` with the seed id, the counts of matched, matched-several and unmatched results, and the unmatched names (public catalog names).

## Risks / Trade-offs

- [A result matches a registered artist that is a different person with the same name, because the intended one is not registered] → only a Verified, active artist whose name no other registered artist has is shown; following it follows that artist, whose name and images the fan sees. Accepted for stage 1; reconsider with the logged data.
- [A catalog alias that is a search hint or a legal name widens the match] → the same single-artist rule applies.
- [Until the daily refresh has read them, existing artists match by name only] → accepted: 30 days. Running the CronJob by hand reads only that day's thirtieth, so it does not shorten this.

## Migration Plan

1. The Atlas migration adds the column, backfills it from `name` and creates the index; merging applies it to prod.
2. Release the backend.
3. Once the rollout has finished, a second migration repeats the backfill for rows whose `known_names` is empty: the previous release keeps registering artists between step 1 and the end of the rollout, and its inserts take the default.
4. Rollback: the column and index are additive; the previous release ignores them and its inserts take `DEFAULT '{}'`. After rolling forward again, the same backfill is applied by one more migration; until then such artists are not found by name.

## Open Questions

- Whether stage 2 (a background lookup of unmatched names in the music catalog) is built: decided from the logged counts once aliases have filled; tracked in an issue (task 3.3).
