## Context

Discovery 画面の `dna-orb-canvas` コンポーネントは Canvas 2D + Matter.js 物理エンジンで構築されている。バブルのヒットテストとテキスト描画は `BubblePhysics.getBubbleAt()` と `DnaOrbCanvas.renderBubbleText()` / `wrapText()` に実装されている。いずれもクラスメソッドに閉じ込められておりユニットテスト不在。

現在のコード状態:
- `getBubbleAt`: `bubbleMap.values()` を順に走査し最初にヒットしたバブルを返す。描画順やタップ中心との距離を考慮しない。
- `wrapText`: スペース区切り (`/\s+/`) でのみ折り返す。CJK テキストはスペースがないため 1 行のまま返る。
- `renderBubbleText`: `minFont=7px` まで縮小してもテキストが `usableWidth` に収まらない場合、`fillText` の `maxWidth` で水平圧縮される。
- `onClick` / `onTouch`: 両方とも `handleInteraction` を呼ぶが、`touchstart` 後の合成 `click` を抑止していない。

## Goals / Non-Goals

**Goals:**
- バブル重なり時に視覚的に最前面のバブル（またはタップ中心に最も近いバブル）が選択される
- タッチデバイスで 1 タップ = 1 follow を保証する
- 日本語等 CJK アーティスト名が読みやすいフォントサイズで複数行に折り返される
- ヒットテスト・テキスト折り返しのロジックに対するユニットテストを追加する

**Non-Goals:**
- 確認 UI (follow 前の確認ダイアログ) や undo 機能の追加
- Matter.js の物理パラメータ調整によるオーバーラップ解消
- バブルサイズのアーティスト名長による動的調整
- E2E テストの追加（ユニットテストでロジックを検証する）

## Decisions

### Decision 1: ヒットテストを「最も中心に近いバブル」方式に変更

**選択:** タップ座標から全バブルの中心までの距離を計算し、ヒット範囲内で最も中心に近いバブルを返す。

**代替案:**
- Z-order（描画順）で最前面を優先 → 描画順は `bubbleMap` のイテレーション順で明示的な Z-order 管理がない。描画順の追跡を新たに導入する必要がありコスト高。
- ヒット半径を 85% に縮小 → 重なり時の根本的な解決にならない。

**理由:** 「中心に近い方」はユーザーの意図と最も一致する。追加のデータ構造不要で既存の `getBubbleAt` のループ内で実現できる。

### Decision 2: タッチイベント処理を `pointerdown` に統一

**選択:** `click` + `touchstart` の 2 リスナーを廃止し、`pointerdown` 1 本に統一する。

**代替案:**
- `touchstart` で `preventDefault()` → iOS Safari でスクロール抑止の副作用リスク。
- タイムスタンプベースのデバウンス → 状態管理が複雑化。

**理由:** Pointer Events API は touch/mouse/pen を統一するための標準 API。二重発火の根本原因を排除できる。Canvas は `touch-action: manipulation` を設定して 300ms delay も防止する。

### Decision 3: CJK 文字単位折り返しの追加

**選択:** `wrapText` 内で CJK 文字（Unicode 範囲判定）を検出し、スペースがないテキストを文字単位で `measureText` しながら折り返す。

**代替案:**
- `Intl.Segmenter` (書記素クラスタ分割) → Safari 16+ で対応しているが、セグメント境界が単語区切りではなく文字区切りのため、ここでは不要な複雑さ。
- 固定文字数で折り返し → フォントやバブルサイズに依存するため不正確。

**理由:** Canvas `measureText` で実際の描画幅を計測しながら折り返すのが最も正確。CJK 判定は `\p{Script=Han}` 等の Unicode property escape で行える。

### Decision 4: テスト可能な純粋関数の抽出

**選択:** 以下の関数を `dna-orb-canvas.ts` / `bubble-physics.ts` からモジュールレベルの export 関数として抽出する。

| 抽出する関数 | 元の場所 | テスト対象 |
|-------------|---------|-----------|
| `findClosestBubble(bubbles, x, y)` | `BubblePhysics.getBubbleAt` | ヒット判定 |
| `wrapText(text, maxWidth, measureFn)` | `DnaOrbCanvas.wrapText` | テキスト折り返し |
| `computeBubbleFont(name, radius, measureFn)` | `DnaOrbCanvas.renderBubbleText` | フォントサイズ決定 |

`measureFn` は `(text: string) => number` として注入し、テスト時にモック可能にする。

### Decision 5: minFont を 7px → 10px に引き上げ

**理由:** CJK 折り返しが入ることでフォント縮小の頻度は大幅に減るが、安全弁として最小フォントサイズを 10px に引き上げる。WCAG の推奨最小サイズ (9px 相当) も満たす。

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| `pointerdown` 統一で既存の keyboard/mouse 挙動に影響 | keyboard は独立の `keydown` リスナーで処理済み。`pointerdown` は mouse click も包含するため互換性あり。Canvas に `touch-action: manipulation` を設定。 |
| CJK 判定の Unicode 範囲が不完全 | ひらがな・カタカナ・CJK 統合漢字・ハングルの主要範囲をカバー。稀な文字は最悪フォールバック（縮小）で表示される。 |
| `minFont=10px` で小バブル内にテキストが収まりきらない | 最小バブル半径 30px → usableWidth 48px。10px フォントで CJK 4-5 文字/行。3 行で 12-15 文字表示可能。大半のアーティスト名をカバー。 |
| 純粋関数抽出によるリファクタリング範囲 | クラスメソッドの内部実装を外部関数に委譲するだけで、公開 API は変更しない。 |
