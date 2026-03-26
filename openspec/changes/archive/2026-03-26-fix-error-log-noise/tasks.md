## 1. backend: Gemini HTTP 499 のコード分類を修正

- [x] 1.1 `gemini/errors.go` の `toAppErr` switch に `case 499: code = codes.Canceled` を追加
- [x] 1.2 `gemini/errors_internal_test.go` に HTTP 499 と context.Canceled のマッピングテストを追加

## 2. backend: DB レイヤーのエラー隠蔽を除去

- [x] 2.1 `rdb/errors.go` の default fallback を `codes.Internal` AppErr から `fmt.Errorf` に変更

## 3. backend: slog デフォルトハンドラーを JSON に設定

- [x] 3.1 `di/provider.go` の `InitializeApp` で `provideLogger` 後に `slog.SetDefault(logger.Slog())` を呼ぶ
- [x] 3.2 `di/consumer.go` の `InitializeConsumerApp` で `provideLogger` 後に `slog.SetDefault(logger.Slog())` を呼ぶ
- [x] 3.3 `di/job.go` の `InitializeJobApp` で `provideLogger` 後に `slog.SetDefault(logger.Slog())` を呼ぶ

## 4. 検証

- [x] 4.1 `make check` を実行し、lint + テストが通ることを確認
