## 1. パフォーマンス計測イベント型定義

> **注意：** `analytics-events.ts` の `_eventPropsMapCoverage satisfies Record<EventName, unknown>` ガードにより、`Events` マップへのエントリ追加と `EventPropsMap` への型追加は **必ず同一コミット** で行う。どちらか一方だけコミットすると TypeScript ビルドが壊れる。

- [x] 1.1 `analytics-events.ts` に `web.vitals` イベント（name: 'LCP'|'INP'|'CLS', value: number, rating: 'good'|'needs-improvement'|'poor', navigation_type: string, route: string）を `Events` と `EventPropsMap` に同時追加する。
- [x] 1.2 `analytics-events.ts` に `perf.long_animation_frame` イベント（duration_ms: number, top_function: string, top_script: string, route: string）を `Events` と `EventPropsMap` に同時追加する。
- [x] 1.3 `analytics-events.ts` に `perf.slow_interaction` イベント（interaction_type: string, duration_ms: number, route: string）を `Events` と `EventPropsMap` に同時追加する。

## 2. 計測コードの実装

- [x] 2.1 `npm install web-vitals` を追加し、`main.ts` の `bootstrap()` 後半（`au.start()` 完了後、`au.container.get(IAnalyticsService)` でインスタンス取得）に `onLCP` / `onINP` / `onCLS`（`'web-vitals/attribution'` ビルド）を登録して PostHog へ送信する。
- [x] 2.2 `main.ts` に Long Animation Frames API Observer を登録する。**フレーム duration ≥ 100ms の場合のみ** `perf.long_animation_frame` を PostHog へ送信する（50〜99ms のフレームは計測されない）。`PerformanceObserver` が非対応環境では `'PerformanceObserver' in window` でガードする。
- [x] 2.3 `main.ts` に Event Timing API Observer を登録する。**Observer 登録時は `durationThreshold` を指定せずブラウザのデフォルト（104ms 固定）を使う**。コールバック内で `entry.duration >= 150` でフィルタリングしてから `perf.slow_interaction` を PostHog へ送信する（`durationThreshold: 150` と書いてはいけない — ブラウザは 104ms 未満を拒否するが 150 は有効なので 104〜149ms が漏れる）。

## 3. バブル上限 50 修正

- [x] 3.1 `bubble-physics.ts` の `addBubbles()` 先頭ループ内に `if (this.bubbleMap.size >= MAX_BUBBLES) break` のキャップガードを追加する。`MAX_BUBBLES = 50` は `services/bubble-pool.ts` の `BubblePool.MAX_BUBBLES` と同じ値として定数化するか、同ファイルからインポートする。
- [x] 3.2 `dna-orb-canvas.ts` の `artistsChanged()` 内 non-ghost パスの **先頭**（`revealGhostBubbles` 呼び出し前）で、`bubbleMap` にある現在の実ボディ ID セットと新アーティスト ID セットの差分を取り、差分ボディを `fadeOutBubble()` でフェードアウトする。`isFadingOut=true` のボディは既に除去処理中なので差分対象から除外する。差分除去後に `revealGhostBubbles(newVal)` を呼び、overflow を `addBubbles` する。

## 4. テスト

- [x] 4.1 `bubble-physics` ユニットテスト：`addBubbles` が 50 ボディ到達後に追加しないことを確認。
- [x] 4.2 `discovery-route` ユニットテスト：再入場（キャッシュあり）→ バックグラウンド更新後に `physics.bubbleCount` が 50 を超えないことを確認。

## 5. 検証・出荷

- [x] 5.1 `make check` グリーン確認。
- [x] 5.2 frontend PR → CI グリーン → マージ → Release → prod ロール確認。
- [x] 5.3 PostHog に `web.vitals` / `perf.long_animation_frame` / `perf.slow_interaction` イベントが届いていることを確認。
- [x] 5.4 specification リポジトリへの spec sync PR を作成・マージする（openspec archive コマンドが新 spec を `openspec/specs/` に同期する PR を自動生成する）。
- [x] 5.5 OpenSpec change をアーカイブ。
