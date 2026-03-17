## Context

Frontend の HTML テンプレート（Aurelia 2）で `<div>` が 94 箇所使用されており、semantic タグは 42 箇所のみ。
CSS は CUBE CSS に準拠しているが、DOM 構造が冗長なため不要なクラスやネストが発生している。

現状の CSS は `@scope` でコンポーネント分離されており、要素セレクタへの変更は影響範囲が限定的。

## Goals / Non-Goals

**Goals:**
- 全テンプレートで `<div>` を適切な semantic HTML 要素に置き換える
- 不要な wrapper div を削除しネスト深度を減らす
- CSS セレクタを semantic 要素に合わせて簡素化する
- web-design-specialist / CUBE CSS スキルルールへの完全準拠

**Non-Goals:**
- 見た目やレイアウトの変更
- TypeScript ViewModel ロジックの変更
- 新規コンポーネントの作成
- Tailwind CSS への移行

## Decisions

### 1. `<div popover>` → `<dialog>` 変換方針

`<dialog>` は popover 属性と互換性があり、ブラウザの top-layer 管理とフォーカストラップを自動で得られる。
`<div popover>` は HTML 仕様上 valid だが、`<dialog>` の方が semantic に正しく、スクリーンリーダーがランドマークとして認識する。

**対象**: coach-mark, notification-prompt, pwa-install-prompt, discovery-route (onboarding-guide)

**代替案**: `role="dialog"` を div に付与 → 却下。native `<dialog>` で得られるフォーカス管理を手動実装する理由がない。

### 2. アクション領域のマークアップ

dialog/card 内のボタングループは `<footer>` とする。
`<dialog>` 内の `<footer>` は「ダイアログのアクション領域」として慣例的に使われ、ARIA パターンにも合致する。

### 3. Settings ページの構造

`.settings-row-start` / `.settings-row-end` パターンは `<dl>` / `<dt>` / `<dd>` に置き換えない。
理由: settings row はトグルやリンクを含む複合的な UI であり、definition list の semantics に合致しない。
代わりに、各行を `<label>` または `<button>` としてマークアップし、内部の div を削減する。

### 4. Semantic 要素の選択基準

| 現状のパターン | 置き換え先 | 根拠 |
|--------------|-----------|------|
| `<div class="*-actions">` (dialog内) | `<footer>` | dialog のアクション領域 |
| `<div class="*-content">` (dialog内) | 削除（直接子要素に） | 不要な wrapper |
| `<div class="sheet-hero">` | `<figure>` | 画像コンテンツの wrapper |
| `<div class="search-results">` | `<section>` | 独立したコンテンツ領域 |
| `<div class="genre-chips">` | `<fieldset>` | フィルタ用の選択肢グループ |
| `<div class="selector-section">` | `<section>` | 独立したコンテンツ領域 |
| `<div class="selector-grid">` | `<div>` (変更なし) | CSS Grid レイアウトコンテナ。子要素の `<button>` がセマンティクスを担う |
| `<div role="status" aria-busy>` | `<output role="status">` | 動的に更新されるステータス |
| `<div class="ticket-row">` | `<article>` | 独立した意味を持つコンテンツ |
| `<div class="artist-identity">` | `<header>` | アイテムのヘッダー情報 |
| `<div class="state-center">` | `<section>` | 独立したコンテンツ領域 |

### 5. CSS 変更方針

- semantic 要素への変更に伴い、`.class` セレクタを要素セレクタ（`footer`, `figure` 等）に置き換えられる場合は置き換える
- ただし `@scope` 内でのみ。グローバルな要素セレクタは作らない
- 不要になったクラス名は削除する

## Risks / Trade-offs

- **[レイアウト崩れ]** → semantic 要素（`<footer>`, `<section>` 等）のデフォルト display がブロックのため、既存の flex/grid レイアウトに影響しない。ただし `<fieldset>` はブラウザデフォルトの border/padding があるため、reset.css での対応を確認する。→ 既存 reset.css で `fieldset { border: 0; padding: 0; }` が設定済みか確認する
- **[E2E テスト破損]** → Playwright テストが `div` セレクタに依存している場合は更新が必要。→ テスト内の div セレクタを検索し、影響範囲を事前に把握する
- **[popover → dialog 変換の動作差異]** → `<dialog popover>` は `<div popover>` とほぼ同じ動作だが、`<dialog>` はデフォルトで `display: none` のため、CSS で `:popover-open` 時の display を明示する必要がある場合がある。→ 各コンポーネントで動作確認する
