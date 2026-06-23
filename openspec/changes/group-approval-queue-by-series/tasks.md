## 1. ViewModel — grouping logic

- [ ] 1.1 Add `PendingSeriesGroup` and `PendingArtistGroup` interfaces to `approval-queue-route.ts`
- [ ] 1.2 Implement `groupQueueByArtistAndSeries(concerts: PendingConcert[]): PendingArtistGroup[]` in `approval-queue-route.ts`, grouping by `performer.name` then `title.value`, computing `dateCount` and `unresolvedCount` per series
- [ ] 1.3 Replace `rows: QueueRow[]` with `groups: PendingArtistGroup[]` on `ApprovalQueueRoute`; update `attached()` / `load()` to call the grouping function
- [ ] 1.4 Update `isEmpty` getter to check `groups.length` instead of `rows.length`
- [ ] 1.5 Update `approve()`, `startReject()`, `cancelReject()`, `confirmReject()` to remove a row and prune empty series/artist groups (mirrors `removeRow` pattern in `approved-concerts-route.ts`)

## 2. Template — grouped layout

- [ ] 2.1 Replace flat `<table repeat.for="row of rows">` with artist `<section>` / series `<details>` / inner `<table>` structure
- [ ] 2.2 Remove Artist and Title columns from the inner table; promote them to group headers
- [ ] 2.3 Add `<summary>` showing series title, date count, and unresolved-venue count (`⚠ N unresolved`)
- [ ] 2.4 Preserve all remaining inner-table columns (Local date, Start time, Listed venue, Resolved venue, Source, Discovered, Actions) and the inline reject form

## 3. Styles

- [ ] 3.1 Add styles for artist heading, series `<details>` / `<summary>`, and unresolved-venue badge in `approval-queue-route.css` (follow the pattern in `approved-concerts-route.css`)

## 4. Tests

- [ ] 4.1 Update or replace the existing `approval-queue-route` unit tests to cover: grouping of concerts by artist and title, `unresolvedCount` computation, row removal pruning empty series/artist groups
- [ ] 4.2 Run `make check` and confirm lint + tests pass
