## Context

PSI Mobile スコア 28/100（TBT 2,660ms、20 Long Tasks）の Discovery ページのボトルネック特定と、physics バブル上限超過バグの修正を行う。

### 既存インフラ
- **PostHog** (`IAnalyticsService.capture`)：全ページで動作、型安全。`analytics-events.ts` に型定義を追加するパターン確立済み。
- **OTEL logger**：error/fatal のみスパン生成。info レベルは console のみ → 本番計測には使わない。
- **`monitorPerformance()`**（`dna-orb-canvas.ts`）：30フレーム平均 FPS を計算し qualityScale を調整する仕組みが既存。
- **`analytics-events.ts`**：`EventPropsMap satisfies` による compile-time カバレッジ保証がある。`Events` と `EventPropsMap` は **必ず同一コミット** で拡張すること（どちらか片方だと `satisfies` ガードでビルドが壊れる）。

## Decisions

### 計測コードの配置場所

`bootstrap()` 後半（`au.start()` 完了後）に配置する。`IAnalyticsService` の DI 解決が必要なため、`au.container.get(IAnalyticsService)` でインスタンスを取得してから Observer を登録する。`_pwaEa` / `_pwaI18n` と同じモジュールレベル変数パターンを踏襲する。

**consent / オプトアウトについて：** `IAnalyticsService.capture()` は内部でオプトアウト済みユーザーの送信を抑制する。ただし `PerformanceObserver` と web-vitals のコールバック自体はオプトアウトに関係なく実行され続ける（送信はされない）。CPU 消費は微小なので許容トレードオフとする。将来的にオプトアウト時に Observer を登録しないようにする改善余地はある。

### web-vitals.js のバージョン・インポート方式

`web-vitals` の attribution build (`'web-vitals/attribution'`) を使用。LCP / INP / CLS の attribution（どの要素が LCP か等）が取得でき、PostHog でのデバッグ精度が上がる。Soft Navigation は Chrome 151+（July 2026 正式リリース）で計測可能、iOS Safari は未対応 — `navigation_type` プロパティで区別する。

### Long Animation Frames のフィルタリング

**100ms 以上のフレームのみ送信。** LoAF のデフォルト閾値は 50ms（視覚的ジャンクの開始点・Long Tasks API と同値）だが、Discovery ページのような physics アニメーションでは低スペック端末で 50〜99ms フレームが頻発し PostHog のイベント量とコストが増大するリスクがある。100ms は 2 フレーム分の遅延（明確なジャンク）を示すため、**50〜99ms の軽微なジャンクは PostHog から見えない** トレードオフを受け入れてコストを抑える。計測初期フェーズでは 100ms で運用し、必要に応じて下げる。

### Event Timing のフィルタリング

INP の poor 閾値（200ms）付近、**150ms 以上のインタラクションのみ送信**。

**実装上の注意：** ブラウザは Event Timing の `durationThreshold` を 104ms 未満に設定できない（104ms = 8ms 刻みで 100ms より大きな最初の値、セキュリティ上の制約）。`durationThreshold: 150` と書くと 104〜149ms のイベントが観測されなくなるため、**Observer 登録は `durationThreshold` を省略（デフォルト 104ms 適用）し、コールバック内で `entry.duration >= 150` フィルタを掛ける**。

### バブル上限修正の方針

2 層の防御策：

1. **`addBubbles` のキャップ**（防御的ガード）：ループ先頭で `this.bubbleMap.size >= 50` なら `break`。`50` は `BubblePool.MAX_BUBBLES`（`services/bubble-pool.ts`）と同値の定数としてインポートするか、同ファイル内で定義する。

2. **`artistsChanged` の旧ボディ差分除去**（根本修正）：non-ghost パスの **先頭**（`revealGhostBubbles` 呼び出しより前）で差分を取り除く。これにより `revealGhostBubbles` が返す overflow の `addBubbles` 呼び出しにも旧ボディ除去が先行する。

### 旧ボディ検出のロジック

```
現在のリアルボディIDセット = bubbleMap のキー
                          （__ghost__ プレフィックスと isFadingOut=true を除く）
新アーティストIDセット = newVal の id
削除対象 = 現在のリアルボディIDセット - 新アーティストIDセット
```

`isFadingOut=true` のボディは既に除去アニメーション中なので差分対象から除外する（再度 `fadeOutBubble()` を呼んでも idempotent だが不要な副作用を避ける）。

差分除去は `artistsChanged` の non-ghost パス先頭で実行し、その後 `revealGhostBubbles(newVal)` → overflow の `addBubbles` と進む。

## Open Questions

- Long Animation Frames の 100ms 閾値は初期設定。PostHog でデータが集まったら 50ms まで下げてより細かい分析ができるか評価する。
