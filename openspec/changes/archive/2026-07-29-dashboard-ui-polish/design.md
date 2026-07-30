## Context

ダッシュボードは Aurelia 2 SPA のメインルートで、`concert-highway`（レーザービーム・日付グループ）、`artist-filter-bar`（絞り込み bottom sheet）、`page-header`（ヘッダー）、`snack-bar`（全画面通知）、`bottom-sheet`（汎用シートプリミティブ）が組み合わさって構成される。今回の変更はすべて frontend のみで、proto/RPC/BSR の変更は伴わない。

## Goals / Non-Goals

**Goals:**

- PWA 更新スナックバーのアクションボタンを視覚的に強調し、ユーザーが更新を見逃さないようにする
- レーザービームエフェクトのユーザー制御（デフォルト off）を実現し、不快なユーザーを救済する
- コンサートリストで月・年の境界を視覚的に伝え、時間軸上の位置を直感的に把握できるようにする
- 絞り込みシートがアーティスト数に依存せずチケット状況と完了ボタンを常に表示できるようにする
- Bottom sheet の swipe dismiss を体感的に速く、誤操作（バウンスバック）のないものにする

**Non-Goals:**

- Settings ページへのビーム設定の同期（localStorage のみで完結）
- アーティストリストのタブ UI への移行（今回は max-height + scroll のみ）
- Bottom sheet の全面的なジェスチャー制御リファクタリング
- テーマ・カラー設定など他の表示カスタマイズ機能

## Decisions

### D1: ビームトグルを page-header スロットに配置し、DashboardRoute が状態を所有

**選択肢:**
- A) `artist-filter-bar` 内部に toggle を追加（フィルターシートまたは trigger 隣）
- B) `dashboard-route.html` の `<page-header>` スロットに直接 toggle ボタンを追加
- C) Settings ページに移動

**決定: B**

`artist-filter-bar` は `display: contents` なので host の flex コンテキストに直接流れ込む。`DashboardRoute` にビーム状態を持たせることで、`artist-filter-bar` への不要な結合を避けられる。C は発見しにくい。ヘッダーに隣接配置することで「フィルターと同列の表示制御」として直感的に機能する。

### D2: localStorage キー `liverty:beams:enabled`、デフォルト false

既存の `StorageKeys` enum（`src/constants/storage-keys.ts`）に `beamsEnabled` を追加し、命名規則（`liverty:` prefix + kebab-case）を踏襲する。`DashboardRoute.attached()` で読み込み、`toggleBeams()` で書き込み。初回訪問時（キー未設定）は false 扱い。

**理由:** ビームは視覚的に強い演出であり、多くのユーザーが望むとは限らない。デフォルト off にすることで不快感を避け、使いたいユーザーが積極的に有効化する設計とする。

### D3: Spotlight アイコンを `svg-icon.html` に `case="spotlight"` として追加

既存の svg-icon コンポーネントは switch/case パターンで管理。新しいアイコンを同じ方法で追加し、他のアイコンと一貫した管理にする。アイコン形状はステージライト（ハウジング矩形 → 台形ヘッド → 三角コーン → 底辺ライン）。

### D4: `DateGroup` に `isFirstOfMonth` / `monthSeparatorLabel` フィールドを追加

`protoGroupToDateGroup` は個別グループを変換するため月の前後比較ができない。`toDateGroups` で変換後に `lastMonthKey` を比較して `isFirstOfMonth` を付与する。ラベル（"2026年7月"）は `toDateGroups` 内で `Date.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long' })` から生成し、`monthSeparatorLabel` に格納する。

`concert-highway.html` の `repeat.for` 内でグループ `<li>` の先頭に `if.bind="group.isFirstOfMonth"` の separator div を挿入する。discriminated union より `DateGroup` フィールド追加の方が変更範囲が小さい。

### D5: Bottom sheet — 3段階の dismiss 改善

1. `--_duration: 160ms`（240ms から短縮）: close アニメーション自体を速くする最小コスト変更
2. `onSnapChange` で dismiss-zone 検出時に `scrollArea.style.pointerEvents = 'none'` をセット: スナップ後のバウンスバックを封じる
3. `pointerup` イベントで scroll 位置が `scrollTop / maxScroll < 0.25` なら即 `requestClose()`: snap-settle を待たず早期クローズ。`scrollsnapchange` 未対応ブラウザ（Safari）でも一貫した動作になる

`onClose` で `pointer-events` をリセット（次回 open に備えて）。

## Risks / Trade-offs

- **`DateGroup` インターフェース変更** → `concert-highway.spec.ts` の fixture を更新する必要がある。フィールドを optional にして後方互換を保つことも可能だが、今回は required にして snapshot テストの更新で対処する
- **`pointerup` 早期クローズの誤発火** → ユーザーがシート内をスクロール中に誤って dismiss される可能性。閾値を `< 0.25`（25% 以下）と低めに設定し、通常のスクロール操作では発火しないようにする。`dismissable` フラグで非解除シートは完全にスキップ
- **`pointer-events: none` が onClose 前に解除されない場合** → `requestClose()` → `closeDialog()` → `onClose()` の同期チェーンで `onClose` 内でリセットするため問題なし。ただし `detaching()` でも確実にリセットする

## Migration Plan

1. 全変更が frontend 単一リポジトリのみ → 単一 PR で完結
2. localStorage `liverty:beams:enabled` は新規キーのため既存ユーザーへの影響なし（未設定 = false のまま）
3. `DateGroup` 型変更は型安全なので、コンパイルエラーで漏れを検出できる
4. Rollback: PR を revert するだけで完結（永続副作用は localStorage の新規キーのみ）
