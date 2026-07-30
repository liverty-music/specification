## Why

ダッシュボードのイベントカード（matched状態）に適用されているレーザービームライトのにじんだ光（box-shadow glow）が少し強すぎるため、`--_spot-glow` の alpha 値を下げて視覚的な圧迫感を軽減する。

## What Changes

- `event-card.css` の `--_spot-glow` CSS カスタムプロパティの alpha 値を `70%` から `50%` に変更する

影響範囲：
- matched カードの box-shadow Layer 2（上方向にじみ）
- matched カードの box-shadow Layer 4（全周にじみ）
- matched カードのロゴ drop-shadow 中間層
- matched カードのテキスト text-shadow 中間層

## Capabilities

### New Capabilities

なし

### Modified Capabilities

なし（実装の詳細のみの変更、spec-level の要件変更なし）

## Impact

- **frontend**: `src/components/live-highway/event-card.css` 1行変更
- API・バックエンド・プロトコル変更なし
- ビジュアルリグレッションテスト（visual baselines）の更新が必要
