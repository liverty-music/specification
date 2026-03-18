## Context

`coach-mark` コンポーネントは app-shell に1つだけ配置され、`@aurelia/state` Store 経由で `targetSelector` / `active` がバインドされる。Store の `clearSpotlight` dispatch は `spotlightTarget = ''` と `spotlightActive = false` を同時に設定するが、Aurelia のバインディング更新順序は非決定的であり、`targetSelectorChanged()` が `activeChanged()` より先に発火するケースがある。

## Goals / Non-Goals

**Goals:**
- `querySelector` に空文字が渡されることによる `InvalidSelectorError` を防止する
- Aurelia のバインディング更新順序に依存しない堅牢な実装にする

**Non-Goals:**
- Store の状態設計の変更（`spotlightTarget = ''` は「ターゲットなし」のセマンティクスとして妥当）
- `dashboard-route.ts` の `laneIntroSelector` getter の変更（呼び出し元のガードは正しく機能している）

## Decisions

### 修正箇所: `coach-mark.ts` の `findAndHighlight()` に入力バリデーション追加

**選択肢:**

| Option | 内容 | 評価 |
|--------|------|------|
| A. `findAndHighlight()` に早期リターン | `if (!this.targetSelector) return` を先頭に追加 | **採用** — 防御的、1行、副作用なし |
| B. `targetSelectorChanged()` にガード追加 | `if (!this.targetSelector) { this.deactivate(); return }` | 過剰 — deactivate は `activeChanged` の責務 |
| C. Store で `spotlightTarget` を nullable に | `null` のときバインディングが変わらないようにする | 過剰 — Store 設計を変える必要がある |

**理由:** Option A は `querySelector` の呼び出し元として入力を検証する責務を果たす。Aurelia のバインディング順序という外部要因に依存しない設計になる。

## Risks / Trade-offs

- **リスク:** 空セレクタを silent に無視するため、将来的に本来空であるべきでないケースも見逃す可能性がある
  → **緩和:** 既存の `MAX_RETRY_MS` 超過時のエラーログで検出可能。空セレクタはリトライ自体が不要なので、リトライループに入らず即座にリターンする方が正しい
