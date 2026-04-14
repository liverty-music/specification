## 1. Reset CSS: アンカー要素のアンダーライン除去

- [x] 1.1 `frontend/src/styles/reset.css` の `:where(a)` に `text-decoration: none` を追加する

## 2. Dashboard: 日付セパレーターのフォントサイズ改善

- [x] 2.1 `frontend/src/routes/dashboard/dashboard-route.css` の `.date-separator time` の `font-size` を `var(--step--2)` から `var(--step-0)` に変更する

## 3. 検証

- [x] 3.1 `make check` を実行し、lint・テストが通ることを確認する（既存のlint警告・TSエラーあり。今回の変更箇所には問題なし）
- [x] 3.2 ブラウザで bottom-nav-bar のアンダーラインが消えていることを目視確認する (user)
- [x] 3.3 ブラウザでダッシュボードの日付セパレーターの可読性が改善されていることを目視確認する (user)
