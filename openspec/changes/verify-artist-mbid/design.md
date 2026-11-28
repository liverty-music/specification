## Context

See proposal.md - Why. The current code:

- `ArtistUseCase.Search`, `ListTop` and `ListSimilar` (backend `internal/usecase/artist_uc.go`) take Last.fm results, drop entries without an MBID (`entity.FilterArtistsByMBID`), and `persistArtists` registers the rest (`ArtistRepository.Create`, which announces `ARTIST.created`). `ListTop` and `ListSimilar` leave out ended artists, also on a 6-hour cache hit (`withoutEndedNow`); `Search` does not, and its cache is returned as stored.
- The event consumer `refresh-artist` runs `ArtistUseCase.Refresh` on `ARTIST.created`: one MusicBrainz lookup, then `UpdateName` and `UpdateActivityEnded`. The daily CronJob `artist-refresh` runs `Refresh` for one thirtieth of the artists.
- The Last.fm client asks `artist.getsimilar` by MBID when one is stored (`lastfm/client.go:161`). On 2026-11-28, `artist.getsimilar` with sumika's right MBID (bc731e96) answered error 6 "The artist you supplied could not be found", while the namesake MBID Last.fm returns for sumika answered its similar artists; Ado and Penthouse answered with either MBID.
- Change correct-artist-mbid added `artists.other_mbids` (no row holds a value in production), `ArtistRepository.UpdateMBID` under the advisory lock it shares with `Create`, `ArtistUseCase.CorrectMBID` and the command `worker artist correct-mbid`.
- The MusicBrainz client throttles to 1 request per second per process (`musicbrainz/client.go`, `rateLimitInterval`); MusicBrainz limits each source IP to 1 request per second on average (https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting) and needs no API key. Last.fm needs an API key and publishes no numeric limit.
- Per-workload "ERROR Log" alert policies exist for Fan API, Event Consumer and Artist Refresh (cloud-provisioning `src/gcp/components/monitoring.ts`).

## Goals / Non-Goals

**Goals:**
- One identifier per meaning: the MBID Last.fm files an artist under, and the artist's own MusicBrainz MBID.
- Every artist a fan is offered was checked against MusicBrainz namesakes, and an artist that cannot be checked automatically reaches the owner through an alert and the admin console.
- No new MusicBrainz call that the existing flow did not already make, other than the namesake search and the official-site reads of namesakes.

**Non-Goals:**
- Re-verifying artists that are Verified or Ambiguous. An admin's choice is never overwritten automatically.
- Changing how concert search chooses artists.

## Decisions

### D1. `listening_mbid` beside `mbid`, replacing `other_mbids`

`artists.listening_mbid TEXT NOT NULL UNIQUE` holds the MBID Last.fm returns for the artist; `artists.mbid` stays the MusicBrainz MBID of the real artist. Both are equal until the MBID is corrected. Last.fm results are matched against either column (`ListByMBIDs`, `Create`), and `Artist.ListSimilar` asks Last.fm with `listening_mbid`. `other_mbids` is dropped.

The spec calls Last.fm "the listening service" and the attribute `listening_mbid`, because vendor names stay out of specs and proto (`rpc-design` skill, "Identifiers"); the column and Go field follow the spec (`ListeningMBID`).

Alternative rejected: keep `other_mbids` and let `ListSimilar` ask with an other MBID when one exists. It mixes "MBIDs the artist was corrected from" with "the key Last.fm uses", and a second correction would leave the choice of key undefined. History of earlier MBIDs has no reader: a search matches by the Last.fm MBID, which never changes.

Uniqueness: an MBID is the `mbid` or `listening_mbid` of at most one artist (one artist may hold the same value in both). `Create` and `UpdateMBID` check it under the advisory lock correct-artist-mbid introduced (`pg_advisory_xact_lock` on one constant key, taken first in both transactions), so a registration of a Last.fm MBID cannot interleave with a correction that frees or takes it. The two unique indexes back the check.

### D2. `mbid_status` and who sets it

`artists.mbid_status TEXT NOT NULL CHECK (mbid_status IN ('unverified','verified','ambiguous'))`, default `unverified`.

| writer | from | to |
|---|---|---|
| `Artist.Create` | (new) | the status it is given; `ListTop`, `ListSimilar` and `ArtistUseCase.Create` give Unverified (Create is the fan `ArtistService.Create`, open to any signed-in caller, so its MBID is checked like any other), `Search` gives the verified result |
| `ArtistUseCase.VerifyMBID` via `UpdateMBID` (with the catalog's name and activity status, in the same write) | Unverified | Verified |
| `ArtistUseCase.VerifyMBID` via `MarkMBIDAmbiguous` | Unverified | Ambiguous |
| `ArtistUseCase.CorrectMBID` via `UpdateMBID` | any | Verified |

`VerifyMBID` reads the artist first (`Artist.Get`) and does nothing unless it is Unverified, so the consumer skips an artist `Search` already verified, and a daily run never touches an admin's choice. Two runs on the same Unverified artist (the consumer and the daily job) compute the same result; the second write repeats the first.

Alternative rejected: carry the status on the `ARTIST.created` payload and skip there. The consumer would still need a read for the daily path, and the payload is the fan-facing `entity.v1.Artist`, which has no reason to show the status.

### D3. The verification decision

For an artist with name N and MBID M (both from Last.fm):

1. `Artist.ListNamesakes(N)`: MusicBrainz `GET /ws/2/artist?query=artist:"N"`, keeping results whose name equals N ignoring case. Each candidate carries MBID, name, country, life span and disambiguation (`entity.CatalogArtist`).
2. Candidates other than M = 0 → Verified with M. (M not among the results is treated the same: the search index lags, and M is what Last.fm vouches for.)
3. Otherwise, read each candidate's official homepage (`Artist.ListOfficialSiteRelations` + `Artist.SelectOfficialSite`, M included). Exactly one candidate has one → `UpdateMBID` to it (it may be M) and Verified. Zero or more than one → `MarkMBIDAmbiguous`, and log at ERROR `artist MBID is ambiguous` with the artist id, name and candidate MBIDs.

Then, for a Verified result, read the catalog's name and activity status of the final MBID (`Artist.GetArtist`) and store MBID, name, `activity_ended` and Verified with one `UpdateMBID` (one `UPDATE`, inside the advisory-lock transaction of D1); for a corrected artist the same statement clears images, official site and check time (correct-artist-mbid D3). Every catalog read happens before the write, so a failed read leaves the artist Unverified and the retry or the daily run decides again. Writing the status first and the name afterwards was rejected: a failure between them leaves a Verified artist with the listening service's name, and the retry skips it because it is no longer Unverified. `Search` does the same reads before `Artist.Create` and registers the match with the catalog's name and activity status.

The official-homepage rule picked the intended artist in all 7 known wrong cases of the correct-artist-mbid audit; the rule was derived from the same 7 cases, so it is kept narrow (exactly one candidate) and every other case goes to a person.

Calls per artist: 2 MusicBrainz requests with no namesake (search, lookup), plus 1 per candidate with namesakes. The MusicBrainz client's existing throttle and retry apply; a failure other than "not found" fails `VerifyMBID` and leaves the artist Unverified.

### D4. Where VerifyMBID runs

- Event consumer `refresh-artist` on `ARTIST.created` runs `VerifyMBID` instead of `Refresh` (up to 3 retries, then the poison queue, as today). Ambiguous returns success: the ERROR log fires the Event Consumer ERROR Log alert, and a retry would decide the same.
- The CronJob `artist-refresh` first runs `VerifyMBID` for every Unverified artist (`Artist.ListByMBIDStatus`), oldest first, then its slot of `Refresh` as today, under the same stop rules (3 consecutive failures, shutdown). It catches artists whose announcement exhausted its retries and, once after the migration, all existing artists. Its ERROR Log alert covers Ambiguous results there.
- `ArtistUseCase.Search` runs the same decision for each match it is about to register, before `Artist.Create`, and registers the match with the decided MBID and status (Verified or Ambiguous). A match whose decision fails (MusicBrainz unavailable) is registered Unverified and not returned; the consumer verifies it. The Fan API ERROR Log alert covers Ambiguous results there.

A decision that corrects M to an MBID another artist already holds returns that artist from `Create`: the new Last.fm MBID is not stored, so the next search after the 6-hour cache decides again. Accepted: it costs one decision per 6 hours for such a name, and no row is wrong.

### D5. Read-time filter

`Search`, `ListTop` and `ListSimilar` return only artists with `mbid_status = verified` and `activity_ended = false`. The status comes with the rows `ListByMBIDs` returns, and a reused cached result is re-read with one `ListByMBIDs` call (the existing `withoutEndedNow` path, extended; `Search` gains it). The fan RPC and the frontend change nothing.

### D6. Admin console: Artist MBIDs screen

New admin RPCs on `rpc.admin.artist.v1.ArtistService`:

| RPC | request | response | usecase |
|---|---|---|---|
| `ListByMbidStatus` | `mbid_status` (required, `ArtistMbidStatus`) | `artists` (`entity.v1.Artist`) | `ArtistUseCase.ListByMBIDStatus` |
| `CatalogArtistService.ListByArtist` (new service `rpc.admin.catalog_artist.v1`) | `artist_id` | `catalog_artists` (`entity.v1.CatalogArtist`) | `CatalogArtistUseCase.ListByArtist` |
| `CorrectMbid` | `artist_id`, `mbid` | `artist` | `ArtistUseCase.CorrectMBID` |

The screen (`admin/artist-mbids/`, nav entry "Artist MBIDs") reads every value from these responses: the artist's name and MBID from `ListByMbidStatus.artists[].name/mbid`; each candidate's MBID, name, country, life span, disambiguation and official homepage from `CatalogArtistService.ListByArtist.catalog_artists[]`. It links each candidate's MBID to its MusicBrainz page so the admin can check details the list does not show. Candidates are read live when an artist is opened, not stored: an Ambiguous artist is rare, and stored candidates would go stale.

`CatalogArtistUseCase.ListByArtist` runs D3 steps 1 and 3 for the artist (search, then official homepage per candidate). It lives on a CatalogArtist service and usecase because it returns CatalogArtists, not Artists (`rpc-design` skill: a read of another resource goes to that resource's service); `ListBy<Key>` because `artist_id` is a required field that selects the set.

### D7. Removals and documentation

- `worker artist correct-mbid` (backend `cmd/worker`) and its DI and tests are removed; cloud-provisioning `docs/runbooks/correct-artist-mbid.md` is removed and its links updated.
- The Last.fm client doc comment (`lastfm/client.go`, "Usage Guidelines") is rewritten from https://www.last.fm/api/tos and https://www.last.fm/api/intro (read 2026-11-28): 3.1 non-commercial use only (liverty-music/backend#953); 2.3 storage under the law of the country of residence, 4.3 caching per the HTTP headers (the comment's "permanent storage is prohibited" is not in the current terms); 4.4 limits set at Last.fm's discretion with no published number, and the intro page's warning against "continuously making several calls per second". The throttle stays at 200 ms (5 requests per second), the value chosen when the client was written; the comment says so.

## Risks / Trade-offs

- [Every existing artist starts Unverified, so discovery is nearly empty until the daily job has verified them] → the job is started by hand right after the migration (`kubectl create job --from=cronjob/artist-refresh`); about 5,500 artists at 2 or more MusicBrainz requests each take 3 to 4 hours. The product has no users yet (owner and one tester), so this is accepted instead of marking existing rows Verified unchecked.
- [Search latency: each new match costs 2 or more MusicBrainz requests at 1 per second] → only matches not registered yet are verified, after the Last.fm MBID filter (sumika: 30 results, 6 with an MBID). Task 6.3 measures it on prod; if a first search of a common name exceeds 15 seconds, verify only the first matches in catalog order and register the rest Unverified.
- [The Fan API, the event consumer and the daily job share one egress IP and each throttles only itself] → MusicBrainz answers 503 above the limit; the client retries with backoff, and a failed verification leaves the artist Unverified for the next run.
- [The official-homepage rule picks a wrong namesake] → only when exactly one candidate has a homepage; the admin can correct on the screen, and the corrected MBID is kept by every later run.
- [An Ambiguous artist an Organizer represents cannot be found by admin Search] → the admin resolves it on the Artist MBIDs screen first.

## Migration Plan

1. Proto release (CatalogArtist, ArtistMbidStatus, admin RPCs), BSR generation.
2. Backend migration: add `listening_mbid` (backfill from `mbid`), `mbid_status` (default `unverified`), unique index on `listening_mbid`; set Penthouse's `listening_mbid` to `c94eaf81-baae-465d-8197-9951c2ef52cd`, the MBID Last.fm's `artist.search` returned for "Penthouse" on 2026-11-28 (MusicBrainz: the UK indie rock band, 1995-10 to 2002-11), after checking read-only that no row holds it as `mbid`; drop `other_mbids`. The migration matches Penthouse's row by its current `mbid`, read from prod when the migration is written. Merge applies it to prod (AtlasMigration).
3. Release the backend; start the daily job by hand; watch its log until the Unverified count reaches 0, and read the Ambiguous artists.
4. Frontend admin screen release; the owner resolves the Ambiguous artists, including the six of liverty-music/backend#920 if the rule did not.
5. cloud-provisioning: remove the runbook.

Rollback: the migration is not reversible for `other_mbids` (empty in production). Rolling the backend back to v1.160.0 needs the column back; restore it with an empty default.
