## Why

Discovery 画面のアーティストバブル UI に 2 つの UX バグがある。

1. **誤タップ**: バブルが密集して重なっている状態で 1 つをタップすると、隣接バブルも follow されてしまう。ヒットテスト (`getBubbleAt`) がイテレーション順で最初にヒットしたバブルを返し、Z-order（描画順）を考慮していない。また、`touchstart` と合成 `click` の二重発火を防止していない。
2. **CJK テキスト視認性**: 「ポルカドットスティングレイ」等のスペースなし日本語アーティスト名が `wrapText` で折り返されず、`minFont=7px` まで縮小された上で `fillText` の `maxWidth` で水平圧縮される。読めないレベルの視認性になっている。

どちらもモバイルユーザーの onboarding 体験を直接損ねており、早急な修正が必要。

## What Changes

- `getBubbleAt` のヒットテストを改善: タップ座標に最も中心が近いバブルを返すよう変更
- タッチイベントの二重発火を防止 (`touchstart` 後の合成 `click` を抑止)
- `wrapText` に CJK 文字単位の折り返しを追加
- `minFont` の下限を引き上げ (7px → 10px)
- ヒットテストとテキスト折り返しロジックをテスト可能な純粋関数として抽出
- 各バグを検知するユニットテスト (Vitest) を追加

## Capabilities

### New Capabilities

(なし)

### Modified Capabilities

- `artist-discovery-dna-orb-ui`: バブルのタッチ認識精度要件とテキスト表示の CJK 折り返し要件を追加

## Impact

- `frontend/src/components/dna-orb/bubble-physics.ts` — `getBubbleAt` ロジック変更
- `frontend/src/components/dna-orb/dna-orb-canvas.ts` — イベントハンドラ、`wrapText`、`renderBubbleText` 変更
- 新規テストファイル追加 (`bubble-physics.spec.ts`, `dna-orb-canvas.spec.ts` or similar)
- バックエンド・インフラへの影響なし
