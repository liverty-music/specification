## Why

Discovery ページがスマートフォンで重く（PSI Mobile スコア 28/100、TBT 2,660ms、20 Long Tasks）、ボトルネックが未特定のため改善効果を測定・検証できない。加えて、再入場 + バックグラウンド更新の組み合わせで physics エンジンのバブルが仕様上限 50 を超えるバグがある（`artistsChanged` が既存ボディを削除しないまま新ボディを追加するため）。

## What Changes

### パフォーマンス計測基盤（全ページ対象）
- **Long Animation Frames API** を `bootstrap()` に登録。50ms 超フレームが発生したルート・原因関数名を PostHog に送信。Discovery 以外（Dashboard、Tickets 等）でも自動収集。
- **web-vitals.js**（`npm install web-vitals`）を追加。LCP / INP / CLS を実ユーザーから継続収集し PostHog に送信。Soft Navigation 対応版で SPA ルートごとの計測も可能。
- **Event Timing API** を登録。100ms 超のインタラクション遅延を PostHog に送信。INP の詳細デバッグに使用。
- `analytics-events.ts` に `web.vitals`・`perf.long_animation_frame`・`perf.slow_interaction` の3イベントを型安全に追加。

### Discovery バブル上限 50 修正
- **`addBubbles` にキャップを追加**：`physics.bubbleMap.size >= MAX_BUBBLES` で追加を止め、physics エンジンが 50 ボディを超えないようにする。
- **`artistsChanged` に古いボディ掃除を追加**：real（非 ghost）アーティストセットに差し替わる際、physics に残っている旧ボディのうち新セットに含まれないものを fade-out で除去する。

## Impact

- **Frontend のみ**。backend / proto / BSR 変更なし。
- 計測コードは非ブロッキングで追加。本番パフォーマンスへの副作用なし。
- バブル上限修正は再入場シナリオで発生していた過多ボディを解消し、physics の計算量が仕様通りに抑えられる。
