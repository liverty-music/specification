## Context

See proposal.md for the problem. Today `artists.mbid` is `NOT NULL` with a unique index, `persistArtists` (shared by Search, ListSimilar and ListTop) registers every catalog match whose MBID is unknown, and no operation changes an MBID. On 2026-11-26 Ado, Aimer, Yama, Sumika, Saji and Penthouse carried a namesake's MBID; Penthouse was corrected by hand in the database. The catalog lookup used by Search keeps returning the namesake's MBID for those names, so a corrected artist would be registered a second time.

The catalog cannot tell which same-named person a fan means, so the right MBID is a human judgement. The design therefore does not try to detect namesakes in the request path; it makes a correction possible, durable and complete.

## Goals / Non-Goals

**Goals:**
- A correction survives later searches: the wrong MBID finds the corrected artist.
- A correction removes everything that was read from the namesake.
- Every registered artist is checked once, and the wrong ones are corrected.

**Non-Goals:**
- Detecting a namesake automatically in Search or Refresh (no signal in the catalog separates same-named people).
- Merging two artist rows. A correction to an MBID another row already has fails; the owner resolves the duplicate by hand.
- An admin console screen or an RPC. Corrections are rare (6 known in the first month); a command is enough.

## Decisions

### D1. `artists.other_mbids TEXT[]`, not a separate table

`other_mbids TEXT[] NOT NULL DEFAULT '{}'` with a GIN index and a `COMMENT ON COLUMN`, as `events.other_listed_venue_names` does for venue names. Lookups use `a.other_mbids @> ARRAY[t.mbid]`, so the index serves them. `entity.Artist` gains `OtherMBIDs []string`. Alternative: an `artist_other_mbids(mbid PRIMARY KEY, artist_id)` table, which makes cross-artist uniqueness a database rule but adds a join to every artist query and a second entity; rejected because corrections are rare and `UpdateMBID` checks uniqueness under the lock of D3.

### D2. Resolution by any MBID the artist has had

`ListByMBIDs` returns each artist whose `mbid` or `other_mbids` holds one of the given MBIDs, once, ordered by the first given MBID that matches it. `Create` treats a given MBID that is in some artist's `other_mbids` as registered: its insert skips those MBIDs and the fetch-back returns that artist for them. `persistArtists` builds its lookup from every MBID of each returned artist (its own and its other MBIDs), so a match under a replaced MBID maps to the corrected artist, and a result lists an artist once even when two matches resolve to it.

### D3. `UpdateMBID` and the lock shared with Create

`ArtistRepository.UpdateMBID(ctx, id, mbid)` runs in one transaction:
1. `pg_advisory_xact_lock(<artist-mbid key>)`, the same lock `Create` takes before its insert. Rows it protects: the set of MBIDs of all artists. `Create` is the only other path that adds an MBID to the set, so a search cannot register the replaced MBID between the check and the update.
2. `SELECT mbid, other_mbids FROM artists WHERE id = $1 FOR UPDATE` (NotFound when absent).
3. Unchanged when the given MBID is the artist's own.
4. AlreadyExists when another artist has the given MBID as `mbid` or in `other_mbids`.
5. `UPDATE`: `mbid` = given, `other_mbids` = (old `other_mbids` minus the given MBID) plus the replaced MBID; `fanart`, `fanart_sync_time`, `official_site_check_time` to NULL, `activity_ended` false; and `DELETE FROM artist_official_site WHERE artist_id = $1`.
Nothing is announced: no consumer reads a correction. The unique index on `mbid` still guards a lost race with a path that does not take the lock.

Clearing is what makes the later jobs repair the artist: the fanart sync takes artists with no sync time, the official-site refresh takes followed artists with no check time and registers the right site, and `CorrectMBID` reads the name and `activity_ended` at once. A site a fan registered by hand is lost with the namesake's; the refresh finds the right one from the catalog.

### D4. `CorrectMBID` order

`ArtistUseCase.CorrectMBID(ctx, artistID, mbid)`: reject an MBID that is not 36 characters (InvalidArgument), read the artist (NotFound), look the MBID up in the catalog (`Artist.GetArtist`; NotFound means a typo and stops before anything is stored), `UpdateMBID`, then `refresh` with the new MBID and the artist's name so the name and `activity_ended` follow the right person. A refresh failure is returned (Unavailable) after the correction is stored; running the command again with the same MBID changes nothing and repeats the refresh, so the admin repairs it by running it again.

### D5. Entry point: a worker command, runbook in cloud-provisioning

`worker artist correct-mbid <artist id> <mbid>`, run like the `workflow` commands: `kubectl exec deploy/workflow-worker -n backend -- /worker artist correct-mbid ...`, as the worker's database identity, printing the artist as JSON. DI builds only the artist repository, the MusicBrainz client and the use case (as the artist refresh job does). Alternative: an admin RPC. Rejected: it needs a proto Release and BSR generation, and a console screen to be usable, for an operation that runs a few times in total.

### D6. The audit is operational

For every registered artist, read the catalog record of its MBID (name, type, country, life span, disambiguation) and the other catalog artists with exactly the same name, and list the artists whose name has another candidate. A person decides from the list (country, life span, the concerts the artist has) which MBID is right. The list and the decisions go in the task's report, not in an issue (artist names are public, but follower counts are not). Wrong artists are corrected with the command of D5; those are production writes the owner approves one by one.

## Risks / Trade-offs

- [A person picks the wrong MBID] → `CorrectMBID` shows the catalog's name and `activity_ended` in its output, and the same command corrects it again; the earlier MBID stays in `other_mbids`.
- [A corrected artist's old MBID is the right one for another real artist the catalog returns later] → that artist is never registered under the old MBID. Accepted: the same name reaches the same Last.fm MBID only through the namesake this correction records.
- [`Create` takes a global advisory lock] → creates are rare (new artists only) and short; a search that registers nothing never reaches `Create`.
- [A correction clears the official site] → the refresh registers the right one on its next run, within a day for a followed artist.

## Migration Plan

1. The Atlas migration adds the column and index (backward compatible; the column defaults to empty).
2. Release the backend, check read-only that the migration is `Ready` and the rollout finished.
3. Run the audit (D6), then correct the wrong artists with the owner's approval, and check read-only that each corrected artist has the new MBID and name, that its replaced MBID is in `other_mbids` and that no second row exists under it.
Rollback: the column is additive; the command is not run until the owner asks.
