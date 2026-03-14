## Context

SetHype RPC に `not_in: [3]` の protovalidate ルールが設定されており、HYPE_TYPE_NEARBY を拒否している。しかし仕様（passion-level spec, hype-inline-slider spec）は4段階すべてを正規ティアとして定義している。フロントエンドは仕様通り4段階スライダーを実装済みで、Nearby 選択時に 500 エラーが発生する。

## Goals / Non-Goals

**Goals:**
- Nearby ティアを SetHype RPC で受け入れ可能にする
- フロントエンドの hype 関連定数の命名を統一する

**Non-Goals:**
- Nearby の通知ロジック実装（距離ベース判定は別スコープ）
- Hype ティアの追加・削除
- バックエンドの hype entity/mapper/repository 変更（既に Nearby 対応済み）

## Decisions

### 1. Proto validation rule の削除

`follow_service.proto` の `SetHypeRequest.hype` フィールドから `not_in: [3]` を削除する。`defined_only: true` と `required: true` は残す。

**理由**: Nearby は仕様で定義された正規ティア。DB スキーマ (`CHECK (hype IN ('watch', 'home', 'nearby', 'away'))`)、Go entity、mapper すべてで既に対応済みであり、Proto の validation rule だけが矛盾していた。

### 2. フロントエンド命名統一

`my-artists-page.ts` の4つの定数を以下のように整理する：

| Before | After |
|--------|-------|
| `HYPE_META` | `HYPE_TIERS` |
| `HYPE_LEVELS` | 削除（`HYPE_TIERS` から導出） |
| `HYPE_TYPE_TO_STOP` | `HYPE_TO_STOP` |
| `HYPE_STOP_TO_TYPE` | `HYPE_FROM_STOP` |

**理由**: `HYPE_META`, `HYPE_LEVELS`, `HYPE_TYPE_TO_STOP`, `HYPE_STOP_TO_TYPE` は同じ概念を異なる命名規則で表現しており、認知負荷が高い。`HYPE_TIERS` に tier メタ情報と enum 値を統合し、変換 map は `HYPE_TO_STOP` / `HYPE_FROM_STOP` に簡素化する。

## Risks / Trade-offs

- **Nearby 通知未実装**: Nearby を選択可能にするが、距離ベースの通知フィルタは未実装。ユーザーが Nearby を選んでも Home と同等の通知範囲になる → 仕様の Notification Scope "Within 200km" 表記と実際の動作に乖離が生じるが、段階的なロールアウトとして許容する
