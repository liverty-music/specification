## 1. CSS 変更

- [x] 1.1 `frontend/src/components/live-highway/event-card.css` の `--_spot-glow` alpha を `70%` → `50%` に変更する

## 2. ビジュアルリグレッション対応

- [x] 2.1 `make check` を実行してスタイルリントおよびビルドが通ることを確認する
- [x] 2.2 main ブランチの visual-baselines CI アーティファクトを削除して強制再生成する（matched カードの baseline 更新）

## 3. リリース

- [ ] 3.1 frontend PR を作成してマージする
- [ ] 3.2 frontend に GH Release を作成して prod にリリースする
