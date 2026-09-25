# Tasks

No proto/schema change — this change only corrects the "Search reports failures" requirement so it matches the intended error-mapping contract; no BSR/specification-release coordination is required.

## 1. Delta spec (this PR)

- [x] 1.1 Author the `components/usecase/artist/search` MODIFIED Requirements delta for "Search reports failures": Search returns Artist.Search's, Artist.ListByMBIDs' and Artist.Create's errors unchanged (code preserved), with scenarios for Unavailable, ResourceExhausted and DeadlineExceeded catalog failures, verified by `openspec validate artist-search-failure-codes --strict`

## 2. Backend fix (liverty-music/backend#504, tracked and merged in the backend repo)

- [x] 2.1 `ArtistUseCase.Search` stops wrapping `artistSearcher.Search`'s error with `codes.Internal` and returns it unchanged, mirroring `ListSimilar`/`ListTop` (liverty-music/backend#505)
- [x] 2.2 `ArtistUseCase.Search`'s interface doc comment's "Possible errors" lists Unavailable, ResourceExhausted and DeadlineExceeded alongside NotFound
- [x] 2.3 Table-driven usecase test asserting the catalog port's error code (NotFound, Unavailable, ResourceExhausted, DeadlineExceeded, Internal) survives unchanged through Search, annotated with `@spec` markers for this change's scenarios
- [x] 2.4 `make check` (lint + test) passes; merged via liverty-music/backend#505

## 3. Archive (only after the backend PR merges)

- [x] 3.1 Archive this change so the delta from section 1 is synced into the main spec
