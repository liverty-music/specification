## Context

Cloud Monitoring の ERROR ログアラートが以下の理由でノイズを発生させている：

1. **Gemini HTTP 499 の誤分類**: `gemini.toAppErr` の switch に HTTP 499 (Client Cancelled) が含まれず、`codes.Unknown`（server error）にフォールバックしている
2. **DB レイヤーの過剰なエラー分類**: `rdb.toAppErr` が未知のエラー（`context.Canceled` 含む）をすべて `codes.Internal` でラップし、usecase レイヤーでのエラー種別判定を不可能にしている
3. **slog デフォルトハンドラー未設定**: NATS 接続リトライが default slog (TextHandler → stderr) に出力され、GKE が stderr を `severity=ERROR` に昇格している

## Goals / Non-Goals

**Goals:**

- Gemini HTTP 499 を client error として正しく分類する
- infrastructure レイヤーがエラーの種別を隠蔽しないようにする（エラー分類は interceptor の責務）
- NATS 接続リトライログの false positive を解消する

**Non-Goals:**

- Gemini API の `DEADLINE_EXCEEDED` / `invalid JSON` エラー自体の解決（別 change で対応）
- アラートポリシーの条件やフィルターの変更
- `go-apperr` パッケージの変更

## Decisions

### Decision 1: Gemini HTTP 499 を `codes.Canceled` にマッピング

**選択**: `gemini/errors.go` の `toAppErr` switch に `case 499: code = codes.Canceled` を追加。

**理由**: HTTP 499 は Nginx 由来の非標準コードで「クライアントがリクエストをキャンセルした」を意味する。Gemini API がこのコードを返す場合、サーバーの不具合ではないため `codes.Unknown`（server error）ではなく `codes.Canceled`（client error）が適切。`codes.Canceled` は `IsServerError() = false` なので interceptor が ERROR ログを出力しない。

### Decision 2: `rdb.toAppErr` の default fallback を `fmt.Errorf` に変更

**選択**: 未知のエラーは `codes.Internal` の AppErr にラップせず、`fmt.Errorf` でコンテキスト文字列のみ付与して返す。

**理由**: infrastructure レイヤーがエラーを AppErr にラップすると、元のエラー型（`context.Canceled` 等）が `errors.Is` で検出不可能になる。エラーの最終分類とクライアント向け隠蔽は interceptor の責務。infrastructure レイヤーは既知の DB エラー（pgx/pgconn）のみ AppErr にマッピングし、それ以外は透過的に返すべき。

### Decision 3: `slog.SetDefault()` を DI 初期化直後に呼ぶ

**選択**: 各 DI 初期化関数（`InitializeApp`, `InitializeConsumerApp`, `InitializeJobApp`）で `provideLogger` 後に `slog.SetDefault(logger.Slog())` を呼び、グローバル slog ハンドラーを JSON フォーマットに設定する。

**理由**: `messaging/streams.go` の `connectWithRetry` は標準 `slog` パッケージを直接使用しており、custom logger のインスタンスを受け取らない。`slog.SetDefault()` を呼ぶことで、すべての標準 slog 呼び出しが JSON handler を使用し、GKE が severity フィールドを正しく解釈する。

## Risks / Trade-offs

- **`rdb.toAppErr` default 変更の影響**: 未知のエラーが AppErr ではなく素のエラーとして interceptor に到達するため、interceptor の "unhandled error" パスで `connect.CodeUnknown` として処理される。クライアントへのレスポンスコードは同じ（Unknown）だが、ログメッセージが "server error occurred" から "unhandled error occurred" に変わる。
