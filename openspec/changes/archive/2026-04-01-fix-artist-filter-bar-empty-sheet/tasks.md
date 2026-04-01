## 1. Fix FollowServiceClient

- [x] 1.1 In `frontend/src/services/follow-service-client.ts`, inside `listFollowed()`, add `this.followedArtists = result.map((f) => f.artist)` after the result is assembled (both authenticated and guest branches are covered by the single assignment after the if/else block)

## 2. Unit Tests — ArtistFilterBar

- [x] 2.1 In `frontend/src/components/artist-filter-bar/artist-filter-bar.spec.ts`, add test: `followedArtists` が空のとき `openSheet()` 後 `pendingIds` は `[]`
- [x] 2.2 Add test: `followedArtists` が複数のとき `artistNameFor()` が正しく全て解決できる
- [x] 2.3 Add test: `openSheet()` を2回呼んだとき前回の `pendingIds` がリセットされる
- [x] 2.4 Add test: `dismiss()` で存在しない ID を渡しても `selectedIds` が変わらない

## 3. Integration Tests — FollowServiceClient

- [x] 3.1 In `frontend/src/services/follow-service-client.spec.ts` (create if it does not exist), add test: authenticated `listFollowed()` sets `followedArtists` to the mapped Artist array returned by the RPC client
- [x] 3.2 Add test: guest `listFollowed()` sets `followedArtists` from guest storage follows
- [x] 3.3 Add test: `listFollowed()` with empty result sets `followedArtists` to `[]`

## 4. Verification

- [x] 4.1 Run `make lint` in the frontend repo and confirm no errors
- [x] 4.2 Run `make test` in the frontend repo and confirm all new and existing tests pass
- [x] 4.3 Manually open the artist filter bar bottom sheet in the dev server and confirm followed artists are displayed
