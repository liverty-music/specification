## Why

SetHype RPC が HYPE_TYPE_NEARBY (enum 3) を `not_in: [3]` で拒否しており、仕様通りに4段階スライダーを実装したフロントエンドから Nearby を選択すると 500 エラーが発生する。Nearby は正規の Hype ティアであり、拒否は誤り。

## What Changes

- Proto `SetHypeRequest.hype` から `not_in: [3]` バリデーションルールを削除し、Nearby を受け入れ可能にする
- Proto `HypeType.HYPE_TYPE_NEARBY` のコメントから "Reserved for Phase 2" 表記を削除
- フロントエンドの `my-artists-page.ts` で `HYPE_META`, `HYPE_LEVELS`, `HYPE_TYPE_TO_STOP`, `HYPE_STOP_TO_TYPE` を HYPE に統一した命名に整理

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `passion-level`: Nearby ティアの "Phase 2" 制約を撤廃し、Phase 1 から利用可能にする
- `hype-inline-slider`: フロントエンドの hype 関連命名を整理（機能変更なし、コード品質改善）

## Impact

- **Proto**: `follow_service.proto` (validation rule), `follow.proto` (comment)
- **Frontend**: `my-artists-page.ts` (naming consolidation), `hype-inline-slider.ts` (no functional change)
- **Breaking**: None. Nearby 値は既に DB スキーマ・entity・mapper すべてで対応済み
