## Why

Discovery ページの検索バーには 3 つの UX 問題がある。(1) follow ボタンが小さな + アイコンのみでモバイルでタップしにくい、(2) follow 済みアーティストに ✓ / disabled が表示されない（Aurelia のリアクティビティが BubblePool 内部の Set 変更を検知できない dual-state バグ）、(3) follow 後にフィードバックがなく検索画面に留まったままになる。これらを改善し、検索からの follow 体験をバブルタップと同等にする。

## What Changes

- 検索結果の行（result-item）全体をタップ可能領域に変更し、+ アイコンボタンを削除する
- follow 済みアーティストの検索結果に ✓ アイコン + disabled + 視覚的フィードバックを正しく表示する
  - BubblePool.followedIds を public readonly に変更し、テンプレートから Aurelia ネイティブの Set 観測で直接バインド
  - DiscoveryRoute.poolFollowedIds（dual-state コピー）と isArtistFollowed() メソッドを削除
- follow 後にバブルビューへ自動遷移し、吸収アニメーションを再生する
  - 検索モード終了 → canvas resume → バブルエリア上部に一時バブル spawn → AbsorptionAnimator で orb 吸収 → 後続処理（similar artist 追加、concert search）

## Capabilities

### New Capabilities

- `search-follow-absorption`: 検索結果から follow した際のバブルビュー遷移と orb 吸収アニメーションの振る舞い

### Modified Capabilities

- `artist-discovery-dna-orb-ui`: 検索結果 UI の変更（行全体タップ化、+ アイコン削除）と follow 後の自動遷移
- `aurelia-reactivity`: BubblePool.followedIds の公開と Aurelia ネイティブ Set 観測によるテンプレートバインディング

## Impact

- `frontend/src/services/bubble-pool.ts` — followedIds の可視性変更
- `frontend/src/routes/discovery/discovery-route.ts` — poolFollowedIds 削除、onFollowFromSearch フロー変更
- `frontend/src/routes/discovery/discovery-route.html` — テンプレートバインディング変更、result-item 構造変更
- `frontend/src/routes/discovery/discovery-route.css` — result-item のインタラクティブスタイル
- `frontend/src/components/dna-orb/dna-orb-canvas.ts` — 外部からの spawn + 即吸収 API（既存の spawnBubblesAt + absorb を組み合わせ）
