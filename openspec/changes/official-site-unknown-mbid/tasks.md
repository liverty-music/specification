# Tasks

## 1. Entity operation (components/entity/artist/resolve-official-site-url)

- [ ] 1.1 Add a 404 case to the MusicBrainz client's `ResolveOfficialSiteURL` contract test, annotated with the "MBID unknown to the catalog" scenario, and annotate the existing unreachable case with "Catalog unreachable". Verify `go test ./internal/infrastructure/music/musicbrainz/` passes (no client change expected: a 404 already maps to NotFound)

## 2. Usecase (components/usecase/artist/refresh-official-site)

- [ ] 2.1 In `RefreshOfficialSite`, treat `apperr.ErrNotFound` from the resolver as no URL found: log a warning with the artist id and MBID, store nothing and record the check. Add a unit test for the "MBID unknown to the catalog" scenario (resolver mocked to NotFound; `MarkOfficialSiteChecked` called, no site written) and keep "Catalog unreachable" passing. Verify `go test ./internal/usecase/` passes

## 3. Delivery (backend)

- [ ] 3.1 Open the backend PR citing this change, get `make check` and CI green, merge, and cut a release
- [ ] 3.2 After the next 04:00 JST official-site-refresh run in prod, verify from its logs that an artist whose MBID the catalog does not know (the `public-event-page` test-only Artist, once it exists and is followed) is marked checked and no longer counted as failed
