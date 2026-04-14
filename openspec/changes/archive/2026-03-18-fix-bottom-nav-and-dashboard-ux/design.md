## Context

CUBE CSS の `@layer` カスケード順序（reset → global → block）を使用している。現在 reset 層の `:where(a)` は `text-decoration-skip-ink: auto` のみ設定しており、`text-decoration: none` が欠落している。そのため、ブラウザデフォルトの `text-decoration: underline` が残存し、bottom-nav-bar を含む全 `<a>` 要素にアンダーラインが表示される。

ダッシュボードの日付セパレーターは sticky ヘッダーとして `var(--step--2)`（~12px）を使用しているが、コンサートカードの本文（`var(--step-0)` ~16px）より小さく、情報階層が逆転している。

## Goals / Non-Goals

**Goals:**
- reset 層で全 `<a>` 要素のアンダーラインをリセットする
- ダッシュボード日付セパレーターの可読性を改善する

**Non-Goals:**
- bottom-nav-bar のタブ順序変更（Home は左端のまま — 業界慣習に準拠）
- 意図的にアンダーラインを使用しているコンポーネントの変更（auth-callback, event-detail-sheet は block 層で明示指定済み）

## Decisions

### 1. reset 層で `text-decoration: none` を追加する

**選択:** reset.css の `:where(a)` に `text-decoration: none` を追加

**代替案:**
- `.nav-tab` に個別に `text-decoration: none` を追加 → 対症療法であり、他の `<a>` 要素でも同じ問題が再発する可能性がある
- global 層で対応 → reset の責務（ブラウザデフォルトの除去）に合致しない

**理由:** CUBE CSS の設計原則に従い、ブラウザデフォルトの除去は reset 層の責務。block 層で意図的に `text-decoration: underline` を指定しているコンポーネント（auth-callback:52行目, event-detail-sheet:99行目）は、`:where()` より詳細度が高いため影響を受けない。

### 2. 日付セパレーターのフォントサイズを `var(--step-0)` に変更

**選択:** `var(--step--2)` → `var(--step-0)`

**代替案:**
- `var(--step--1)`（~14px）→ 最低限の改善だが、`uppercase` + `letter-spacing` の視覚的縮小を考慮すると不十分
- `font-weight` を上げる → サイズの問題は解決しない

**理由:** sticky セクションヘッダーはコンテンツと同等以上の視認性が必要。`uppercase` + `letter-spacing: 0.05em` は視覚的にフォントサイズを小さく見せるため、`var(--step-0)` が適切。

## Risks / Trade-offs

- **reset で `text-decoration: none` を追加することで、インラインリンクのアンダーラインが消える** → 明示的にアンダーラインが必要な箇所は既に block 層で指定済み。global 層の `text-underline-offset: 0.2em` は装飾用であり、`text-decoration` がない状態では効果なし（副作用なし）
- **日付セパレーターのフォントサイズ増加により、sticky ヘッダーの高さが微増する** → コンサートリストの表示領域がわずかに減少するが、可読性の向上が上回る
