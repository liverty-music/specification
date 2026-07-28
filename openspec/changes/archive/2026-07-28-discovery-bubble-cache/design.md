## Context

Dashboard の `ConcertStore.lastDateGroups` パターンの直接適用。`DiscoveryRoute` はナビゲーションのたびに再インスタンス化されるが、`ArtistStore` は DI シングルトンとしてアプリ寿命で存在する。最後に生成したバブルプールをシングルトンに保持すれば、次回の `DiscoveryRoute` インスタンスが即座にそれを読み取れる。

## Decisions

- **保存するのは最終出力 `Artist[]` であり中間データ（listSimilar 結果 など）ではない。** Dashboard での教訓: 中間データの組み合わせは条件 mismatch のリスクが高い。最終プール（dedup・トップアップ処理済み）をそのまま保存する。

- **キャッシュヒット時はゴーストバブルをスキップ。** 画面が一瞬でも半透明バブルに切り替わることを避け、前回のリアルアーティストが即描画されるべき。

- **バックグラウンド更新はキャッシュヒット時のみ発動。** 初回訪問では `loadInitialBubbles()` がコールドロードを担う（ゴースト→リアルの切り替えアニメーションが走る）。

- **`setBubbles()` は `loadInitialBubbles()` 完了後に呼ぶ。** 失敗・中断時は前回のキャッシュを保持したままとし、古いデータで次回再入場できるようにする。

## Migration

1. `ArtistStore` に `lastBubbles` + `peekBubbles()` + `setBubbles()` を追加。
2. `DiscoveryRoute.loading()` にキャッシュ分岐を追加。
3. `loadInitialBubbles()` 完了時に `setBubbles()` を呼ぶ。
