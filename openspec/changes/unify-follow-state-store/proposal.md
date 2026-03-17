## Why

Discovery ページの follow 状態が `BubblePool.followedIds` (Set)、`DiscoveryRoute.followedArtists` (配列)、`@aurelia/state` Store の `guest.follows` (onboarding 時) の 3 箇所に分散しており、follow/rollback 時に 4 箇所を手動同期する必要がある。これは `improve-search-bar` change で表面化したリアクティビティバグの根本原因であり、follow ロジックの正確性とテスタビリティを確保するために状態管理を `@aurelia/state` Store に一元化する。

## What Changes

- `AppState` に `discovery` slice を追加: `followedArtists: FollowedArtist[]` を管理
- `AppAction` に `discovery/follow` と `discovery/unfollow` アクションを追加
- `appReducer` に discovery slice のケースを追加（pure function、テスト容易）
- `BubblePool` から follow 追跡を除去: `followedIds` Set、`markFollowed()`、`unmarkFollowed()`、`isFollowed()` を削除。`dedup()` は `followedIds` を引数で受け取る形に変更
- `DiscoveryRoute` を Store ベースに移行: `followedArtists` と `poolFollowedIds` を削除し、Store state から derived。follow/rollback は `dispatch()` のみ
- テンプレートバインディングを Store state 参照に変更（`@aurelia/state` がリアクティビティを保証）

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `state-management`: `AppState` に `discovery` slice 追加、`discovery/follow` と `discovery/unfollow` アクションを追加
- `bubble-pool-lifecycle`: `BubblePool` から follow 追跡責務を除去し、`dedup` のシグネチャを変更

## Impact

- `frontend/src/state/app-state.ts` — `DiscoveryState` interface と `discovery` slice 追加
- `frontend/src/state/actions.ts` — `discovery/follow`、`discovery/unfollow` アクション追加
- `frontend/src/state/reducer.ts` — discovery slice のケース追加
- `frontend/src/services/bubble-pool.ts` — follow 関連メソッド削除、`dedup(bubbles, followedIds)` に変更
- `frontend/src/routes/discovery/discovery-route.ts` — Store ベースに移行、followedArtists/poolFollowedIds 削除
- `frontend/src/routes/discovery/discovery-route.html` — テンプレートバインディング更新
- 依存: `improve-search-bar` change が先行して完了している前提
