## Why

Discovery ページに遷移するたびに `BubbleManager` が再インスタンス化されてバブルプールが空になるため、フォロー済みアーティストを持つユーザーでも毎回 `listSimilar` ネットワーク RPC が発生し、バブルが表示されるまで 1〜3 秒の空白が生じる。フォローなしユーザーは `ArtistStore.listTop` のキャッシュで即時返るが、フォローありの一般ユーザーでは再入場のたびにスピナーと同等の待ち時間が発生する。

Dashboard の `ConcertStore.lastDateGroups` パターンと同様に、最後に生成されたバブルプール（`Artist[]`）を `ArtistStore` シングルトンに保持することで、再入場時にゴーストバブルをスキップして即座にリアルアーティストを表示できる。

## What Changes

- `ArtistStore` シングルトンに `lastBubbles: Artist[] | null` を追加し `peekBubbles()` / `setBubbles()` を公開。
- `DiscoveryRoute.loading()` でキャッシュ確認: `peekBubbles()` が non-null なら即座にリアルアーティストでプールを初期化（ゴーストバブル不要）し、バックグラウンドで `loadInitialBubbles()` を実行して更新。null の場合（初回訪問）はゴーストバブルを使う現行フロー。
- `loadInitialBubbles()` 完了後に `setBubbles(pool.availableBubbles)` でシングルトンを更新。

## Impact

- Frontend のみ。proto / BSR / backend / API 変更なし。
- 再入場: ゴーストバブルなし → キャッシュからリアルアーティストが即描画 → バックグラウンド更新。
- 初回訪問: ゴーストバブル → ネットワーク取得 → リアルアーティストに切り替え（現行フロー維持）。
