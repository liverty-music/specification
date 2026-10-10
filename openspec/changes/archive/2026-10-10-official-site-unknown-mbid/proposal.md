## Why

When the music catalog has no artist for an MBID (MusicBrainz answers 404), OfficialSiteRefreshUseCase.RefreshOfficialSite fails and records no check. The artist therefore stays due, is picked again by every daily run, fails every time, and counts toward the run's consecutive-failure stop. This happens for an artist whose MBID was removed from the catalog, and for the test-only Artist that `public-event-page`'s production E2E needs (an MBID the catalog does not know, so that no real artist's followers are notified of test concerts).

## What Changes

- Artist.ResolveOfficialSiteURL states that it fails with NotFound when the catalog has no artist for the MBID. The implementation already does this (an HTTP 404 maps to NotFound); only the spec is silent about it.
- OfficialSiteRefreshUseCase.RefreshOfficialSite treats NotFound from Artist.ResolveOfficialSiteURL like "no URL found": it leaves the stored site as it is and records the check, so the artist is checked again only after the usual 7 days. Every other failure still records no check.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/entity/artist/resolve-official-site-url`: adds the NotFound failure for an MBID the catalog does not know.
- `components/usecase/artist/refresh-official-site`: a catalog NotFound records the check instead of failing.

Unchanged, and relied on: `components/entity/artist` (no attribute changes), and the operations Artist.GetOfficialSite, Artist.CreateOfficialSite, Artist.UpdateOfficialSiteURL, Artist.MarkOfficialSiteChecked and Artist.ListStaleOfficialSite, whose behavior is untouched.

## Impact

- **backend:** `internal/usecase/official_site_refresh_uc.go` (branch on `apperr.ErrNotFound` from the resolver) and its tests; a test for the MusicBrainz client's 404 path if one is missing.
- **No proto, schema or frontend change.** Other callers of the resolver (the first-follow site resolution in `follow_uc.go`) already treat any failure as a warning and are unaffected.
