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

`artists.name_keys TEXT[] NOT NULL`, holding the keys of the name and of every alias, without duplicates, with `CREATE INDEX idx_artists_name_keys ON artists USING gin (name_keys)`. `ListByNameKeys` is one query, `WHERE name_keys && $1`; `&&` (overlap) is one of the operators the built-in `array_ops` GIN operator class indexes, and GIN is meant for searching element values inside composite values (https://www.postgresql.org/docs/17/gin.html). The planner may still choose a sequential scan at the current size.

Alternative rejected: a table `artist_names (artist_id, name_key)` with a B-tree. It looks up as fast, but adds a table whose rows must be added and removed with every name change.

Alternative rejected: keep the raw aliases in a second column. Nothing reads an alias except the match.

The cost of GIN is slower writes; artist rows are written on registration, verification, correction and the daily refresh of one thirtieth of them.

### D2. The name key

NFKC normalization (`golang.org/x/text/unicode/norm`), `strings.ToLower`, surrounding white space removed and inner runs collapsed to one space. One entity function derives it for writes and lookups. The migration backfills `name_keys` from `name` with `lower(regexp_replace(btrim(normalize(name, NFKC)), '\s+', ' ', 'g'))`.

### D3. Aliases arrive with the existing artist read

`GetArtist` adds `inc=aliases` and returns every alias name; `entity.Artist` carries the derived `NameKeys`. `UpdateMBID` takes the keys and writes them in its single statement. `Refresh` calls the new `UpdateNameKeys` after `UpdateName`, also when the name did not change, since aliases change on their own. When `GetArtist` returns another canonical MBID or fails, the writers keep their current rules; keys are only taken from a successful read.

Alternative rejected: have `UpdateName` take the keys. The name and the aliases change independently, and `Refresh` skips `UpdateName` when the name is equal.

### D4. Matching in ListSimilar

After the MBID results are registered, one `ListByNameKeys` call takes the keys of every result without an MBID. A result is matched when exactly one returned artist has its key; that artist takes the result's position in the list, once, and is left out when it is the seed. Offered-to-fans filtering and the 6-hour cache apply to it like to any other artist. All registered artists count toward "exactly one", offered or not, so an unoffered namesake does not make the offered one look unique. No lock is needed: nothing is written from a match.

The usecase logs at INFO `similar artists without MBID` with the seed id, the counts of matched, matched-several and unmatched results, and the unmatched names (public catalog names).

## Risks / Trade-offs

- [A result matches a registered artist that is a different person with the same name, because the intended one is not registered] → only a Verified, active artist whose name no other registered artist has is shown; following it follows that artist, whose name and images the fan sees. Accepted for stage 1; reconsider with the logged data.
- [A catalog alias that is a search hint or a legal name widens the match] → the same single-artist rule applies.
- [Until the daily refresh has read them, existing artists match by name only] → accepted: 30 days. Running the CronJob by hand reads only that day's thirtieth, so it does not shorten this.

## Migration Plan

1. The Atlas migration adds the column, backfills it from `name` and creates the index; merging applies it to prod.
2. Release the backend.
3. Rollback: the column and index are additive; the previous release ignores them. Its inserts need the column's default, so the column is declared `NOT NULL DEFAULT '{}'`.

## Open Questions

- Whether stage 2 (a background lookup of unmatched names in the music catalog) is built: decided from the logged counts once aliases have filled; tracked in an issue (task 3.2).
