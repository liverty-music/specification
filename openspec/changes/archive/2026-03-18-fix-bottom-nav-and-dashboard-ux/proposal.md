## Why

Bottom nav bar のラベルテキストにブラウザデフォルトのアンダーラインが表示されており、視覚的ノイズになっている。また、ダッシュボードの日付セパレーターのフォントサイズが小さすぎ（~12px）、sticky セクションヘッダーとしての可読性が低い。情報階層の逆転（ヘッダーが本文より小さい）も発生している。

## What Changes

- **reset.css の `<a>` リセット修正**: `:where(a)` に `text-decoration: none` を追加し、ブラウザデフォルトのアンダーラインを全アンカー要素から除去する
- **ダッシュボード日付セパレーターのフォントサイズ改善**: `.date-separator time` の `font-size` を `var(--step--2)` から `var(--step-0)` に変更し、sticky セクションヘッダーとしての可読性を確保する

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. (CSS スタイル修正のみ。機能要件の変更なし)

## Impact

- `frontend/src/styles/reset.css` — 全 `<a>` 要素のテキスト装飾がリセットされる。意図的にアンダーラインを使用している箇所（auth-callback, event-detail-sheet）は各コンポーネントの `@layer block` で明示的に `text-decoration: underline` を指定済みのため影響なし
- `frontend/src/routes/dashboard/dashboard-route.css` — 日付セパレーターのフォントサイズ変更
