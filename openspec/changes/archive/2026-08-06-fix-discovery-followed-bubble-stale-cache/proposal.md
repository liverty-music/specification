## Why

`ArtistStore.lastBubbles` キャッシュはセッション中にフォローが発生しても更新されないため、
re-entry 時に `peekBubbles()` がフォロー済みアーティストを含む古いプールを返し、そのアーティストのバブルが薄く（opacity 0.4）表示され続ける。
フォロー済みアーティストはバブルフィールドに表示しないというシステム全体の設計方針（`dedup()` による除外）と矛盾する。

## What Changes

- `DiscoveryRoute.loading()` でキャッシュ読み込み時に `followedIds` を使って followed artist をフィルタする（1行追加）
- `DnaOrbCanvas.renderBubble()` の `isFollowed ? opacity * 0.4` 描画パスを削除（上記修正で到達不能になる）
- `discovery-bubble-cache` spec に「キャッシュ再読み込み時は followed artist を除外する」要件を追記

## Capabilities

### New Capabilities

_なし_

### Modified Capabilities

- `discovery-bubble-cache`: re-entry 時のキャッシュ読み込みで followed artist を除外する要件を追加

## Impact

- `frontend/src/routes/discovery/discovery-route.ts` — `loading()` に 1 行フィルタ追加
- `frontend/src/components/dna-orb/dna-orb-canvas.ts` — `renderBubble()` の `isFollowed` opacity 分岐を削除
- 仕様: `openspec/specs/discovery-bubble-cache/spec.md` に要件追記
