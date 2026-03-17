## Why

Frontend の HTML テンプレートで `<div>` タグが過剰に使用されており、semantic HTML 要素への置き換えが不十分。
div:semantic 比率が 2.24:1 と高く、アクセシビリティ（ランドマークナビゲーション）、可読性、CSS セレクタの複雑性に悪影響を与えている。

## What Changes

- `<div popover>` パターンを `<dialog>` 要素に置き換え（coach-mark, notification-prompt, pwa-install-prompt, discovery-route）
- アクション領域の `<div>` を `<footer>` に置き換え（error-banner, hype-notification-dialog, notification-prompt, pwa-install-prompt）
- コンテンツラッパー `<div>` を適切な semantic 要素に置き換え（`<section>`, `<figure>`, `<fieldset>` など）
- ローディング状態の `<div role="status">` を `<section role="status">` または `<output>` に置き換え
- 不要な div ネストの削減（tickets-route, my-artists-route, settings-route, user-home-selector）
- CSS セレクタの簡素化（semantic 要素導入に伴う不要クラスの削除）

## Capabilities

### New Capabilities

（なし — 新規機能の追加ではなく、既存 DOM 構造のリファクタリング）

### Modified Capabilities

（既存 spec の要件変更なし — 実装レベルの HTML/CSS リファクタリングのみ）

## Impact

- **frontend**: 29 HTML テンプレートのうち約 21 ファイルを修正、関連 CSS ファイルのセレクタ調整
- **テスト**: E2E テスト（Playwright）のセレクタが div に依存している場合は更新が必要
- **リスク**: 低 — 見た目・動作の変更なし。semantic 要素のデフォルトスタイルによる意図しないレイアウト崩れに注意
