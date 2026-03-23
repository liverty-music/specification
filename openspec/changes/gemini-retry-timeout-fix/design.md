## Context

SearchNewConcerts RPC は Gemini API (gemini-3-flash-preview + Google Search grounding) を呼び出す。
実測の Gemini 応答時間は 25-110 秒だが、現在のタイムアウトチェーンは以下の通り：

```
Frontend (timeout なし)
  → GKE Gateway  GCPBackendPolicy.timeoutSec = 60s
    → http.TimeoutHandler = 60s (SERVER_HANDLER_TIMEOUT)
      → backoff.Retry (ctx 継承, MaxTries=3)
        → genai.GenerateContent(ctx) ← 60s で ctx 失効 → 504
```

問題点:
1. Gemini の応答時間 (25-110s) に対して Gateway/Handler timeout (60s) が不足
2. `isRetryable` が Google 公式推奨の 408, 500, 502, 504 を含んでいない
3. リトライ時に親 ctx の deadline を共有 → 2回目以降は残り時間が足りない
4. client cancel (画面遷移) で Gemini call が中断される

## Goals / Non-Goals

**Goals:**
- Gemini API 呼び出しが 120 秒以内に完了できる十分な timeout を確保する
- Google 公式リトライ戦略に準拠したエラーリトライを実装する
- ConcertService の timeout を他 RPC から分離し、軽量 RPC への影響を回避する
- client cancel でも Gemini call を中断しない（1 回目から独立 context）
- Gateway → Handler → Gemini の timeout チェーン全体の整合性を確保する

**Non-Goals:**
- SearchNewConcerts の非同期化（将来検討）
- Gemini モデルの変更（gemini-3-flash-preview → GA モデル）
- Frontend 側の timeout 設定（現状 Connect-Web はデフォルト timeout なしで問題なし）

## Decisions

### 1. Gemini API 呼び出しの context を親 RPC から切り離す

**決定**: 1 回目の API コールから `context.WithoutCancel(parentCtx)` + `context.WithTimeout(..., 120s)` で新しい context を作成する。

**理由**:
- client cancel（画面遷移等）で Gemini call を止めたくない
- リトライごとに独立した 120 秒の deadline を確保する
- `context.WithoutCancel` により trace_id/span_id は維持される

```go
backoff.Retry(parentCtx, func() ([]*entity.ScrapedConcert, error) {
    reqCtx, cancel := context.WithTimeout(
        context.WithoutCancel(parentCtx), 120*time.Second)
    defer cancel()
    resp, err := s.client.Models.GenerateContent(reqCtx, ...)
    ...
}, ...)
```

**代替案**: `context.Background()` を使う → trace 情報が失われるため却下。

### 2. isRetryable を Google 公式推奨に合わせる

**決定**: 以下のコードを retryable に追加する。

| Code | 現状 | 変更後 | 理由 |
|------|------|--------|------|
| 408 | - | Retry | Request Timeout (公式推奨) |
| 429 | Retry | Retry | そのまま |
| 500 | - | Retry | Internal Server Error (公式推奨) |
| 502 | - | Retry | Bad Gateway (公式推奨) |
| 503 | Retry | Retry | そのまま |
| 504 | **Not retry** | **Retry** | DEADLINE_EXCEEDED (公式推奨、context 独立化で有効) |

504 を retryable にする根拠: 現状コメントの「retrying wastes 15-25s per attempt」は親 ctx の deadline 残量が不足していたため。context を独立化すれば各リトライが 120s のフレッシュな deadline を持ち、504 のリトライが有効になる。

### 3. backoff パラメータの調整

**決定**:
- `MaxInterval`: 10s → 60s（Google 推奨に合わせる）
- `MaxTries`: 3 のまま（十分なリトライ回数）

### 4. ConcertService 専用の HandlerTimeout 分離

**決定**: ConcertService のパスにのみ 120s の `http.TimeoutHandler` を適用し、他の RPC は 60s のまま。

**実装方法**: `connect.go` の mux 構成で ConcertService のパスだけ別の TimeoutHandler でラップする。

```go
// ConcertService: 120s (Gemini API + grounding の応答時間を考慮)
concertPath, concertHandler := concertHandlerFunc(handlerOpts...)
protectedMux.Handle(concertPath,
    http.TimeoutHandler(concertHandler, concertTimeout, ""))

// Other services: default timeout
for _, hf := range otherHandlerFuncs {
    path, handler := hf(handlerOpts...)
    protectedMux.Handle(path, handler)
}

// Root mux に default timeout を適用
rootHandler := http.TimeoutHandler(rootMux, defaultTimeout, "")
```

### 5. Timeout チェーンの整合性

変更後のタイムアウトチェーン:

```
Frontend (timeout なし — Connect-Web デフォルト)
  → GKE Gateway  GCPBackendPolicy.timeoutSec = 150s  (← 60s から変更)
    → http.TimeoutHandler = 120s (ConcertService 専用)
      → backoff.Retry (parentCtx, MaxTries=3)
        → context.WithTimeout(WithoutCancel(parentCtx), 120s)
          → genai.GenerateContent(reqCtx)

各レイヤーのバッファ:
  Gateway (150s) > Handler (120s) > Gemini timeout (120s/回)
  ※リトライ含む最大所要時間: 120s + backoff(1s) + 120s + backoff(2s) + 120s = ~363s
  ※ただし Handler 120s で全体が打ち切られるため、実質 1回目のみ 120s で完了する必要がある
```

**重要**: Handler の 120s timeout は RPC 全体にかかる。リトライ 3 回 × 120s = 360s は Handler の 120s に収まらない。そのため:
- Gemini context timeout (120s) は Handler timeout と同値
- 1 回目が失敗した場合、2 回目以降は Handler の残り時間で制約される
- ただし Gemini context は `WithoutCancel` なので、Handler timeout 後もバックグラウンドで完了する（レスポンスはクライアントに返せないが、search log の更新は行われる）

**GCPBackendPolicy の timeoutSec**: Gateway timeout は Handler timeout より大きくする必要がある。120s + バッファ = 150s に設定。

### 6. configmap コメントの更新

`SERVER_HANDLER_TIMEOUT` のコメントを実測値に合わせて更新する。

## Risks / Trade-offs

- **[Risk] Handler 120s でも Gemini が完了しない場合がある** → Mitigation: backoff で最大 3 回リトライ。それでも失敗なら graceful degradation（空結果返却）。CronJob 経由では deadline なしで動作するため、最終的にはバッチで補完される。
- **[Risk] `context.WithoutCancel` により、RPC cancel 後も Gemini リクエストが残る** → Mitigation: backoff.Retry の parentCtx は cancel を受け取るため、次のリトライは開始されない。進行中の Gemini コールのみバックグラウンドで完了する（最大 120s）。
- **[Trade-off] Gateway timeout を 150s にすることでスロークライアントが長時間接続を保持する** → 許容範囲: SearchNewConcerts は低頻度（フォロー時のみ）のため負荷は限定的。
