## Context

Discovery ページの検索結果リストは DOM ベースの `<ul>/<li>` で描画され、各行の右端に小さな `<button>` (+ アイコン) が follow のタップ領域となっている。follow 状態は `BubblePool.followedIds` (private Set) と `DiscoveryRoute.poolFollowedIds` (ReadonlySet コピー) の二重管理になっており、テンプレートは `isArtistFollowed()` メソッド経由でバインドしているため Aurelia のリアクティビティが機能していない。

バブルビューでは Matter.js + Canvas 2D でバブルを描画し、タップ時に `AbsorptionAnimator` が Bézier 曲線で orb に吸い込むアニメーションを再生する。検索結果からの follow にはこの演出がなく、無反応のまま検索画面に留まる。

## Goals / Non-Goals

**Goals:**

- 検索結果の行全体をタップ可能にし、モバイルでの操作性を改善する
- follow 済みアーティストの状態を正しくリアクティブに表示する（✓ + disabled）
- 検索から follow した際にバブルビューに戻り、orb 吸収アニメーションで視覚フィードバックを提供する
- follow 状態の dual-state を解消し、BubblePool を single source of truth にする

**Non-Goals:**

- follow 状態管理の Store 統合（別 change `unify-follow-state-store` で対応）
- 検索結果からの連続 follow（follow → similar artist 追加で自然に次の発見につながるため不要）
- 検索 UI 自体のリデザイン（入力フィールド、クリアボタン等は変更しない）

## Decisions

### 1. 行全体タップ化: `<li>` に click handler、`<button>` + `<svg-icon>` を削除

**選択**: `<li>` 要素に `click.trigger` を付与し、follow ボタンと + アイコンを完全に削除する。

**理由**: follow 済みの行は disabled 表示で視覚的に区別されるため、+ アイコンが無くても「タップ = follow」はコンテキスト上自明。ボタンを残すと「ボタンに見えるのに行全体がタップ領域」という UX の矛盾が生じる。

**代替案**: ボタンを装飾的に残す → 混乱の元になるため却下。

### 2. リアクティビティ修正: BubblePool.followedIds を public にし、テンプレートから直接 Set.has() バインド

**選択**: `BubblePool.followedIds` を `public readonly` に変更し、テンプレートで `followedIds.has(artist.id)` を直接バインドする。`DiscoveryRoute.poolFollowedIds` と `isArtistFollowed()` を削除。

**理由**: Aurelia 2 は `Set.has()` をネイティブに観測できる（公式ドキュメント確認済み）。`Set.add()` / `Set.delete()` が呼ばれると `.has()` バインディングが自動再評価される。メソッド呼び出し (`isArtistFollowed()`) はブラックボックスで Aurelia が内部依存を追跡できないため、直接バインドが必要。

**代替案**: `poolFollowedIds` の再代入パターンを活かしテンプレートから参照 → dual-state が残るため却下。Store 統合 → スコープが大きいため別 change に分離。

### 3. DiscoveryRoute に followedIds getter を追加

**選択**: `public get followedIds(): ReadonlySet<string>` を追加し、`this.pool.followedIds` を返す。テンプレートは `followedIds.has(artist.id)` でバインド。

**理由**: `pool` 自体を public にせず、テンプレートに必要な最小限のインターフェースだけ公開する。BubblePool のテスト容易性を損なわない。

### 4. follow 後のバブルビュー遷移 + 吸収アニメーション

**選択**: `onFollowFromSearch()` のフローを以下に変更:

```
onFollowFromSearch(artist)
  ├─ followArtist(artist)          ← optimistic follow
  ├─ exitSearchMode()              ← isSearchMode=false, canvas resume
  └─ dnaOrbCanvas.spawnAndAbsorb(artist, spawnPosition)
       ├─ spawnBubblesAt([artist], x, y)   ← バブルエリアやや上部
       ├─ 即座に absorb 開始
       ├─ orbRenderer.injectColor()         ← on absorption completion
       └─ dispatch 'need-more-bubbles' event ← immediately on spawnAndAbsorb call
```

**spawn 位置**: バブルエリア上部（canvas height の 15-20% 付近）。検索バーの直下に現れ、orb に向かって降りていく軌道が自然。

**理由**: 既存の `AbsorptionAnimator` と `spawnBubblesAt` を組み合わせるだけで実現可能。新規アニメーション実装は不要。

**代替案**: 検索結果上でオーバーレイ再生 → canvas が pause 中のため別レイヤーが必要で複雑。却下。

### 5. dna-orb-canvas に `spawnAndAbsorb()` メソッドを追加

**選択**: 「spawn → 即吸収」を 1 つの public メソッドとして追加する。

**理由**: spawn と absorb を別々に呼ぶと、タイミング制御が呼び出し側に漏れる。物理エンジンにバブルを追加した直後に吸収を開始する一連の処理をカプセル化する。既存の `onArtistSelected` イベントハンドラのロジック（physics remove → absorption start）を再利用。

## Risks / Trade-offs

**[Risk] Aurelia の Set 観測が深いプロパティチェーンで機能しない可能性** → `followedIds` getter 経由のバインドが正しく動作するか、実装時にコンポーネントテストで検証する。問題があれば `pool` を直接 public にするフォールバック。

**[Risk] exitSearchMode → canvas resume のタイミングで spawn が早すぎる** → `requestAnimationFrame` で 1 フレーム遅延させれば解決。canvas の `resume()` は同期的に render loop を再開するため、通常は即座に spawn 可能。

**[Trade-off] + アイコン削除による affordance の低下** → 行全体のホバー/アクティブスタイル（背景色変化、cursor: pointer）で「タップ可能」を伝える。follow 済みは opacity 低下 + ✓ アイコンで明確に区別。
