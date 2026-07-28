## 1. ArtistStore にバブルキャッシュを追加

- [x] 1.1 `ArtistStore` に `lastBubbles: Artist[] | null = null` フィールド、`peekBubbles(): Artist[] | null`、`setBubbles(artists: Artist[]): void` を追加する。

## 2. DiscoveryRoute のキャッシュ分岐

- [x] 2.1 `DiscoveryRoute.loading()` でキャッシュ確認を追加する: `artistClient.peekBubbles()` が non-null なら pool をリアルアーティストで初期化しゴーストをスキップ。null の場合はゴーストバブルを使う現行フロー。
- [x] 2.2 `loadInitialBubbles()` 完了後に `artistClient.setBubbles(bubbles.pool.availableBubbles)` を呼んでシングルトンを更新する。

## 3. テスト

- [x] 3.1 `DiscoveryRoute.loading()` のキャッシュヒット分岐ユニットテスト: peekBubbles non-null → ゴーストなし・即描画。
- [x] 3.2 `ArtistStore.peekBubbles() / setBubbles()` ユニットテスト。

## 4. 検証・出荷

- [x] 4.1 `make check` グリーン確認。
- [x] 4.2 localhost で再入場時にゴーストなし・即描画されることを確認。
- [x] 4.3 frontend PR → CI グリーン → マージ → Release → prod ロール確認。
- [x] 4.4 OpenSpec change をアーカイブ。
