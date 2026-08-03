## 1. フロントエンド実装

- [ ] 1.1 `discovery-route.ts` の `loading()` で `peekBubbles()` 後に `followedIds` フィルタを追加する: `cachedBubbles.filter(a => !this.followStore.followedIds.has(a.id))`
- [ ] 1.2 `dna-orb-canvas.ts` の `renderBubble()` で `isFollowed` による `opacity * 0.4` の描画分岐を削除する（`showFollowedIndicator` / `followedIds` バインダブルが他に利用箇所がなければ合わせて削除）

## 2. 検証

- [ ] 2.1 `make check` グリーン確認
- [ ] 2.2 frontend PR → CI グリーン → マージ → Release → prod ロール確認
