## Why

Cloud Monitoring の ERROR ログアラートが、サーバー起因ではないエラー（Gemini 499 キャンセル）や、誤分類されたログ（NATS リトライの INFO/WARN が stderr 経由で ERROR に昇格）で発火しており、アラートの信頼性が低下している。また DB レイヤーが未知のエラーを一律 `codes.Internal` にラップしており、上位レイヤーでのエラー種別判定を妨げている。

## What Changes

- **Gemini HTTP 499 のコード分類を修正**: `gemini.toAppErr` で HTTP 499 (Client Cancelled) を `codes.Unknown` ではなく `codes.Canceled` にマッピングする。
- **DB レイヤーのエラー隠蔽を除去**: `rdb.toAppErr` の default `codes.Internal` ラッピングを削除し、未知のエラーは `fmt.Errorf` でコンテキスト付与のみ行う。これにより usecase レイヤーで `context.Canceled` 等の判定が可能になる。
- **slog デフォルトハンドラーを JSON に設定**: `provideLogger` 後に `slog.SetDefault()` を呼び、NATS リトライログが stderr テキスト経由で ERROR に誤分類される問題を解消する。

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `app-error-log-alerting`: ERROR ログアラートのノイズ低減。Gemini HTTP 499 が ERROR として記録されなくなり、NATS リトライの false positive が解消される。

## Impact

- **backend** (`gemini/errors.go`): HTTP 499 マッピング変更
- **backend** (`rdb/errors.go`): default `codes.Internal` を `fmt.Errorf` に変更
- **backend** (`di/provider.go`, `di/consumer.go`, `di/job.go`): `slog.SetDefault()` 追加
- **Cloud Monitoring**: アラートポリシー自体の変更なし。ログ側の severity が正しくなることでノイズが減る
