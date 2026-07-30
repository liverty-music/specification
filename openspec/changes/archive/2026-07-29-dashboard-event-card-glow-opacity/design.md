## Context

`frontend/src/components/live-highway/event-card.css` の matched カード状態では、`--_spot-glow` CSS カスタムプロパティ（`oklch(75% 0.4 var(--artist-hue) / 70%)`）が box-shadow・drop-shadow・text-shadow の中間拡散層として使われている。現在の alpha 70% がやや強く、カード周辺のにじみが視覚的に重い。

## Goals / Non-Goals

**Goals:**
- `--_spot-glow` の alpha を `70%` → `50%` に下げ、にじんだ光を軽くする
- 変更は1変数・1行のみ、他のエフェクト層（border・inner glow・beam・outer atmospheric glow）は一切変えない

**Non-Goals:**
- Layer 5 の外側大気グロー（`/25%`）の調整
- beam cone（`::before`）の調整
- アニメーション・インタラクション挙動の変更

## Decisions

**変数一箇所の変更のみ**

`--_spot-glow` は単一のカスタムプロパティで、matched カード内の複数の shadow に参照されている。この変数の alpha を変えることで box-shadow 2層・drop-shadow・text-shadow が一括して薄まり、一貫した調整ができる。各 shadow を個別に変更する必要はない。

## Risks / Trade-offs

- [ビジュアルリグレッション] matched カードの visual baseline が変わるため、CI の visual-baseline テストが差分を検出する → main ブランチ CI の visual-baselines アーティファクトを削除して強制再生成する（既知の手順）
