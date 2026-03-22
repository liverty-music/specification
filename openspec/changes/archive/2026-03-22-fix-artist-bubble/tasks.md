## 1. ロジック抽出とリファクタリング

- [x] 1.1 `bubble-physics.ts` から `findClosestBubble(bubbles: PhysicsBubble[], x: number, y: number): PhysicsBubble | undefined` を export 関数として抽出。ヒット範囲内で最も中心に近いバブルを返すロジックに変更。`getBubbleAt` は内部で `findClosestBubble` を呼ぶだけにする。
- [x] 1.2 `dna-orb-canvas.ts` から `wrapText(text: string, maxWidth: number, measureFn: (text: string) => number): string[]` を export 関数として抽出。CJK 文字判定と文字単位折り返しを追加。
- [x] 1.3 `dna-orb-canvas.ts` の `renderBubbleText` の `minFont` を `7` → `10` に変更。

## 2. タッチイベント統一

- [x] 2.1 `dna-orb-canvas.ts` の `onClick` / `onTouch` リスナーを廃止し、`pointerdown` 1 本に統一。
- [x] 2.2 Canvas の Shadow DOM CSS に `touch-action: manipulation` を追加。

## 3. ユニットテスト

- [x] 3.1 `findClosestBubble` のテストを作成: 重なりなしヒット、範囲外ミス、重なり時に最近接バブル優先、fadingOut 除外、scale=0 除外。
- [x] 3.2 `wrapText` のテストを作成: 英語スペース区切り折り返し、CJK スペースなし文字単位折り返し、CJK+Latin 混合、短い名前は 1 行、空文字。
- [x] 3.3 `minFont=10` の検証: CJK 長文名で `computeBubbleFont` がフォントサイズ 10px 未満に縮小しないこと。

## 4. 検証

- [x] 4.1 `make check` (lint + test) がパスすること。
- [x] 4.2 dev サーバーで CJK 長文名（ずっと真夜中でいいのに。、ASIAN KUNG-FU GENERATION 等）が折り返し表示されることを確認。
- [x] 4.3 密集バブルをタップして 1タップ=1follow（ダブルファイアなし）を確認。
