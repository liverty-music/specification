## Context

The concert discovery job calls `concertUseCase.SearchNewConcerts(artistID)`, which in turn calls `artistRepo.GetOfficialSite(artistID)`. If no record exists in `artist_official_site`, this returns a `NotFound` error and the job skips (or fails for) that artist. Since the Follow RPC never creates an official site record, all newly-followed artists are invisible to the discovery job.

MusicBrainz exposes official site URLs via the `url-rels` include parameter (`GET /ws/2/artist/{mbid}?inc=url-rels`). The existing `musicbrainz.client` already handles MBID-based lookups and rate-limit throttling, making it the natural place to add this resolution.

The existing `entity.ArtistIdentityManager` interface is already injected into `artistUseCase`, but it only covers name normalization (`GetArtist`). Rather than extending that interface with an unrelated concern, a new focused interface is more appropriate.

## Goals / Non-Goals

**Goals:**
- Automatically persist an artist's official site URL when a user follows them.
- Degrade gracefully: Follow succeeds regardless of whether URL resolution succeeds.
- Allow the Gemini concert search to proceed even without a known URL.
- Select the most relevant URL when MusicBrainz returns multiple `official homepage` relations.

**Non-Goals:**
- Updating an existing official site record (no re-resolution on re-follow).
- Supporting official site types other than `official homepage` (social, streaming, etc.).
- Exposing the resolution status to the caller via the Follow RPC response.
- Implementing a full async queue / Pub-Sub (deferred to a future change).

## Decisions

### Decision 1: New `OfficialSiteResolver` interface instead of extending `ArtistIdentityManager`

**Chosen**: Add `entity.OfficialSiteResolver` with a single method:
```go
ResolveOfficialSiteURL(ctx context.Context, mbid string) (string, error)
```
`musicbrainz.client` implements both `ArtistIdentityManager` and `OfficialSiteResolver`. `artistUseCase` gains a new `siteResolver OfficialSiteResolver` field injected at construction.

**Alternative considered**: Extend `ArtistIdentityManager` with the new method.
**Why rejected**: `ArtistIdentityManager` is about identity normalization (name/MBID). Adding a URL-resolution concern violates single responsibility and forces unrelated mock updates in tests.

---

### Decision 2: Goroutine with `context.WithoutCancel` for async resolution

**Chosen**: After `artistRepo.Follow()` succeeds, spawn a goroutine using `context.WithoutCancel(ctx)` to resolve and persist the official site. The Follow RPC returns immediately.

```
Follow(ctx) {
    artistRepo.Follow(userID, artistID)    // must succeed
    bgCtx := context.WithoutCancel(ctx)
    go resolveAndPersistOfficialSite(bgCtx, artist)
    return nil
}
```

**Why `context.WithoutCancel`**: The HTTP request context is cancelled when the response is sent. Using it directly in the goroutine causes `GetOfficialSite` to fail immediately after the response is flushed. `context.WithoutCancel` (Go 1.21+) preserves deadlines/values while detaching cancellation.

**Alternative considered**: Synchronous resolution within the Follow RPC.
**Why rejected**: MusicBrainz enforces 1 req/sec. Blocking the Follow response for an external API call degrades UX. The throttler queue could introduce 1–2+ second latency under concurrent load.

**Alternative considered**: Dedicated Pub/Sub message.
**Why rejected**: Requires additional infrastructure (Cloud Pub/Sub topic, subscriber). The goroutine approach is sufficient for current scale and is explicitly called out as a stepping stone.

---

### Decision 3: Skip `CreateOfficialSite` if record already exists

**Chosen**: The goroutine calls `artistRepo.GetOfficialSite(artistID)` first. If the record exists (`NotFound` is the only "proceed" signal; any other result aborts), it skips creation. This prevents duplicate-key errors on re-follow scenarios.

---

### Decision 4: `official homepage` URL selection from MusicBrainz url-rels

MusicBrainz can return multiple `official homepage` relations for one artist (e.g., current band site, label page, former band name site).

**Selection priority** (first match wins):
1. `ended = false` AND `source-credit` matches `artist.Name` (case-insensitive) → artist's own current site
2. `ended = false` AND `source-credit` is empty → unattributed current site
3. `ended = false` → any active site (fallback)
4. No match → return empty string (no error)

**Rationale**: The `source-credit` field in MusicBrainz identifies which name the relation belongs to. An artist with a former name (e.g., "phatmans after school" → "saji") will have relations from both identities. Matching current name avoids returning an obsolete site. `ended = true` relations are always excluded.

---

### Decision 5: `ConcertSearcher.Search()` accepts nil `officialSite`

**Chosen**: Change `officialSite *entity.OfficialSite` to be nil-safe. When nil, use an alternate prompt variant:

- **With URL**: `"Focus on information related to the official site ({url}) and the provided search results."`
- **Without URL**: `"Search the official website of \"{name}\" and related sources to find concert information."`

`SearchNewConcerts` in `concertUseCase` changes `GetOfficialSite` error handling: `NotFound` → continue with `site = nil`; other errors → still propagate.

## Risks / Trade-offs

- **Goroutine leak on shutdown**: The background goroutine is fire-and-forget. If the process shuts down before MusicBrainz responds, the operation is silently lost. Mitigation: the next Follow attempt (or a future periodic reconciliation job) can re-trigger resolution.

- **No resolution retry**: If MusicBrainz returns an error (rate limit, network), the site remains unresolved. Mitigation: the `SearchNewConcerts` nil-site path allows the job to proceed with degraded quality, and resolution can be retried by implementing a reconciliation job later.

- **Gemini quality degradation**: Without a known URL, Gemini must discover the official site itself, which may increase hallucination risk or miss site-specific schedule pages. Mitigation: this is explicitly a best-effort fallback path, acceptable for MVP.

- **Race on re-follow**: If a user unfollows and re-follows quickly, two goroutines may attempt `CreateOfficialSite` concurrently. The second will encounter `AlreadyExists`. Mitigation: the goroutine checks existence before inserting; any remaining race is handled by treating `AlreadyExists` as a no-op.

## Open Questions

- Should we add a periodic reconciliation job to backfill official sites for artists that were followed before this change? (Scoped out for now — can be a follow-up change.)
