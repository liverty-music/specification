## Why

SearchNewConcerts RPC が Gemini API (gemini-3-flash-preview + Google Search grounding) を呼び出す際、504 DEADLINE_EXCEEDED が頻発してアラートが発生している。根本原因は 2 つ: (1) Gemini + grounding の実測応答時間（25-110秒）に対して Handler timeout（60秒）が不足、(2) Google 公式リトライ戦略に対してリトライ対象エラーコードが不足（504, 500, 502, 408 が欠落）。

## What Changes

- Gemini API 呼び出しの context を親 RPC から切り離し、リトライごとに `context.WithoutCancel(parentCtx)` ベースで 120 秒 timeout の新 context を作成する（client cancel でも Gemini call を止めない）
- `isRetryable` に Google 公式推奨のエラーコード (408, 500, 502, 504) を追加する
- backoff の `MaxInterval` を 10 秒 → 60 秒に引き上げる
- ConcertService の RPC に対してのみ HandlerTimeout を 120 秒に分離する（他の軽量 RPC への影響を回避）
- API Gateway (GKE Gateway) の ConcertService 向けルートの timeout を 120 秒以上に設定する

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `http-retry`: Gemini API 呼び出しのリトライ戦略を Google 公式推奨に合わせ、context 管理とタイムアウトを修正
- `concert-service`: ConcertService RPC の timeout を他サービスから分離して 120 秒に設定

## Impact

- **backend**: `internal/infrastructure/gcp/gemini/errors.go` — isRetryable 拡大
- **backend**: `internal/infrastructure/gcp/gemini/searcher.go` — context 作成ロジック、backoff パラメータ変更
- **backend**: `internal/infrastructure/server/connect.go` — ConcertService 向け HandlerTimeout 分離
- **backend**: `pkg/config/config.go` — ConcertService 用 timeout 設定の追加（必要に応じて）
- **cloud-provisioning**: `k8s/namespaces/backend/base/server/configmap.env` — configmap コメント更新
- **cloud-provisioning**: GKE Gateway HTTPRoute — ConcertService パスの timeout 設定
