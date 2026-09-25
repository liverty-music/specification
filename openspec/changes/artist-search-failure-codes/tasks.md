# Tasks

No proto/schema change — this change only corrects the "Search reports failures" requirement so it matches the intended error-mapping contract; no BSR/specification-release coordination is required.

## 1. Delta spec (this PR)

- [x] 1.1 Author the `components/usecase/artist/search` MODIFIED Requirements delta for "Search reports failures": Search returns Artist.Search's, Artist.ListByMBIDs' and Artist.Create's errors unchanged (code preserved), with scenarios for Unavailable, ResourceExhausted and DeadlineExceeded catalog failures, verified by `openspec validate artist-search-failure-codes --strict`

## 2. Backend fix (liverty-music/backend#504, tracked and merged in the backend repo)

- [ ] 2.1 `ArtistUseCase.Search` stops wrapping `artistSearcher.Search`'s error with `codes.Internal` and returns it unchanged, mirroring `ListSimilar`/`ListTop`
- [ ] 2.2 `ArtistUseCase.Search`'s interface doc comment's "Possible errors" lists Unavailable, ResourceExhausted and DeadlineExceeded alongside NotFound
- [ ] 2.3 Table-driven usecase test asserting the catalog port's error code (NotFound, Unavailable, ResourceExhausted, DeadlineExceeded, Internal) survives unchanged through Search
- [ ] 2.4 `make check` passes

## 3. Archive (only after the backend PR merges)

- [ ] 3.1 Archive this change so the delta from section 1 is synced into the main spec
