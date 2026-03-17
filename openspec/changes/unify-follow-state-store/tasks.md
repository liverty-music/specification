## 1. Store に discovery slice を追加

- [ ] 1.1 `app-state.ts` に `FollowedArtist` interface と `DiscoveryState` interface を追加
- [ ] 1.2 `AppState` に `discovery: DiscoveryState` を追加し、`initialState` に空の `followedArtists` を設定
- [ ] 1.3 `actions.ts` に `discovery/follow` と `discovery/unfollow` アクションを追加
- [ ] 1.4 `reducer.ts` に `discovery/follow` ケースを追加（重複チェック付き）
- [ ] 1.5 `reducer.ts` に `discovery/unfollow` ケースを追加

## 2. BubblePool から follow 追跡を除去

- [ ] 2.1 `BubblePool` から `followedIds` Set、`markFollowed()`、`unmarkFollowed()`、`isFollowed()` を削除
- [ ] 2.2 `dedup()` のシグネチャを `dedup(bubbles, followedIds: ReadonlySet<string>)` に変更
- [ ] 2.3 `reset()` から `followedIds.clear()` を削除

## 3. DiscoveryRoute を Store ベースに移行

- [ ] 3.1 `followedArtists` プロパティを削除し、Store state から derived する getter に置き換え
- [ ] 3.2 `followedIds` getter を Store state の `discovery.followedArtists` から derived する `ReadonlySet<string>` に変更
- [ ] 3.3 `followArtist()` 内の `pool.markFollowed()` を `store.dispatch({ type: 'discovery/follow', artist })` に置き換え
- [ ] 3.4 `followArtist()` 内の rollback を `store.dispatch({ type: 'discovery/unfollow', artistId })` に簡素化
- [ ] 3.5 `pool.dedup()` の呼び出し箇所に `followedIds` を引数として渡すよう修正（loadInitialArtists, reloadWithTag, getSimilarArtists, loadReplacementBubbles）
- [ ] 3.6 `onArtistSelected` と `onFollowFromSearch` 内の `pool.isFollowed()` ガードを Store state チェックに変更
- [ ] 3.7 canvas の `followedIds` bindable に Store derived の `followedIds` getter を渡すようテンプレートを更新

## 4. テスト

- [ ] 4.1 Reducer ユニットテスト: `discovery/follow` で followedArtists に追加されること
- [ ] 4.2 Reducer ユニットテスト: `discovery/follow` で重複 ID が無視されること
- [ ] 4.3 Reducer ユニットテスト: `discovery/unfollow` で followedArtists から削除されること
- [ ] 4.4 BubblePool ユニットテスト: `dedup(bubbles, followedIds)` が followed artist を除外すること
- [ ] 4.5 `make check` が通ることを確認（lint + test）
