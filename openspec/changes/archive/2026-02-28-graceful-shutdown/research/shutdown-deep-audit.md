# Deep Audit: shutdown パッケージ最適化の残課題

**日付**: 2026-02-28
**対象**: pkg/shutdown, 全 cmd/ エントリポイント, 全 io.Closer 実装
**ステータス**: 調査完了・実装待ち

---

## 現状アーキテクチャ

```
  SIGTERM
    │
    ▼
  signal.NotifyContext() → ctx cancelled
    │
    ├─ cmd/api:      select <-ctx.Done() → return nil → defer shutdown.Shutdown(bg)
    ├─ cmd/consumer:  select <-ctx.Done() → return nil → defer shutdown.Shutdown(bg)
    └─ cmd/job:       loop 終了 → defer shutdown.Shutdown(bg)
                              │
                    ┌─────────▼──────────┐
                    │   pkg/shutdown     │
                    │                    │
                    │ 1. drain           │
                    │ 2. flush           │
                    │ 3. external        │
                    │ 4. observe         │
                    │ 5. datastore       │
                    └────────────────────┘
```

---

## 1. CRITICAL: shutdown.Shutdown() にタイムアウト予算がない

全エントリポイントが以下のように呼び出している:

```go
shutdown.Shutdown(context.Background())  // ← デッドラインなし
```

closer がハングした場合、プロセス全体がハングし、K8s が SIGKILL で強制終了する。

### タイムアウト予算の分析

```
   K8s terminationGracePeriodSeconds: 30s (デフォルト!)
   preStop hook:                       0s (未設定)
   ─────────────────────────────────────────────────
   アプリ shutdown に使える時間:        30s

   Phase 1 (drain):
     healthChecker.Close()           → 0s (即座、atomic flag)
     ConnectServer.Close()           → 最大 30s (独自タイムアウト!)
     MemoryCache.Close()             → 最大 ∞ (goroutine 終了待ち)
     HealthServer.Close() [consumer] → 最大 ∞ (タイムアウトなし!)
     Router.Close() [consumer]       → CloseTimeout 依存 (デフォルト 0 = ∞)

   Phase 2 (flush):
     Publisher.Close()               → 不明

   Phase 4 (observe):
     tracerCloser.Close()            → 最大 30s (独自タイムアウト!)

   ─────────────────────────────────────────────────
   最悪ケース: 30s (server) + ∞ (health) + 30s (tracer) = ∞
   ─────────────────────────────────────────────────
   だが K8s は 30s で SIGKILL する!
```

### 根本的な問題

`io.Closer` インターフェースは context を受け取らないため、各 closer が独自にタイムアウトを管理している。
グローバルな deadline を意識していない。

### 解決案

**エントリポイント側で deadline を渡す:**
```go
ctx, cancel := context.WithTimeout(context.Background(), cfg.ShutdownTimeout)
defer cancel()
shutdown.Shutdown(ctx)
```

`pkg/shutdown` の `run(ctx)` は既に ctx をチェックしている（phase 間で `ctx.Err()` を見る）ので、
deadline 付き context を渡すだけで、タイムアウト超過時に残りの phase をスキップできる。

ただし、phase **内** の個別 closer にはこの ctx が伝播しない（`io.Closer.Close()` に context パラメータがないため）。
これは `ConnectServer.Close()` や `tracerCloser.Close()` が独自に timeout を持つ現行方式で許容可能。

---

## 2. HIGH: CronJob ループが SIGTERM で即座に中断されない

```go
for _, artist := range artists {
    // ctx は signal-bound だが、ループ先頭で ctx.Err() をチェックしていない
    if err := app.ConcertUC.SearchNewConcerts(ctx, artist.ID); err != nil {
        // SIGTERM 受信時、ctx は cancelled 状態
        // SearchNewConcerts は context.Canceled エラーを返す
        // ループはこれを通常エラーとして扱い → consecutiveErrors++
        // 3回キャンセルされた呼び出しの後、circuit breaker がようやく停止
    }
}
```

**影響**: shutdown のたびに無駄な Gemini API 呼び出しが最大3回発生する。

**修正案**:
```go
for _, artist := range artists {
    if ctx.Err() != nil {
        break  // SIGTERM 受信、即座に処理中断
    }
    ...
}
```

---

## 3. HIGH: HealthServer.Close() にタイムアウトがない

```go
// health.go
func (h *HealthServer) Close() error {
    h.SetShuttingDown()
    return h.srv.Shutdown(context.Background())  // ← 無期限に待機する可能性
}
```

`ConnectServer.Close()` は `cfg.ShutdownTimeout` を使って timeout を設定しているが、
`HealthServer.Close()` には timeout がない。

Health probe クライアントが接続を保持し続けた場合、`http.Server.Shutdown()` が無期限にブロックする。

**修正案**: `ConnectServer.Close()` と同様に timeout を設定する。
HealthServer は config への依存がないため、固定値（例: 5s）で十分。

---

## 4. HIGH: Router の二重 Close（安全だがノイジー）

Consumer では Router が2つの経路から Close される:

```
   経路 A: ctx cancelled → Router.Run(ctx) が内部的に Router.Close() を呼ぶ
   経路 B: defer → shutdown.Shutdown() → Drain phase → Router.Close()

   タイムライン:
   ──────────────────────────────────────────────────────
   SIGTERM  ctx.Done   run() return    defer 実行
      │        │           │               │
      ▼        ▼           ▼               ▼
            Router.Run     select 終了    shutdown.Shutdown()
            ctx.Done 検知                     │
            内部で Close()                    ▼
                                     Drain: Router.Close()
                                     (2回目, idempotent)
```

Watermill の `Router.Close()` は **idempotent** であることを確認済み
（`r.closed` フラグをロック下でチェック）。クラッシュはしないが:
- Path A の内部 Close と defer のタイミングが競合する
- Path B は既に Close 済みの Router を冗長に Close しようとする
- Watermill のデバッグログに "Already closed" が出力される（ノイズ）

**許容可能**: 実害なし。ただしログノイズの低減のため、Router を Drain phase から除外し、
ctx cancellation による内部 Close に任せる案も検討可能。

---

## 5. MEDIUM: shutdown.Init() に二重呼び出しガードがない

```go
func Init(l *logging.Logger) {
    logger = l  // 2回呼ばれた場合、silent に上書き
}
```

本番では各アプリが1回だけ Init を呼ぶので問題ないが、テストやリファクタリング時に
異なる logger で Init() を呼ぶとサイレントに置換される。

**修正案**: `sync.Once` でガード、または2回目の呼び出しで panic。

---

## 6. MEDIUM: Init() 前に Shutdown() を呼ぶと nil panic

`Shutdown()` → `run()` → `logger.Info()` で nil pointer dereference。

**修正案**: `run()` の先頭で `logger == nil` チェック。
または `Init()` で nil logger を渡された場合に no-op logger をフォールバック。

---

## 7. LOW: Reset() がスレッドセーフでない

`Reset()` はグローバルな `closers` map と `once` を同期なしで変更する。
現在のテストは `t.Cleanup` で順次実行されるため問題ないが、
parallel テストでは race condition の可能性がある。

**現時点では許容可能**: テストのみの関数であり、parallel テストは使用していない。

---

## 8. INFO: genai.Client / googlemaps.Client は Close 不要

- `genai.Client`: HTTP ベースでステートレス。`Close()` メソッドなし。リーク問題なし。
- `googlemaps.Client`: 単純な HTTP クライアントラッパー。明示的な Close 不要。

---

## 9. INFO: Database.Close() の順序は正しい

```go
func (d *Database) Close() error {
    d.Pool.Close()     // 1. プール内の全接続を閉じる
    d.dialer.Close()   // 2. その後 PSC トンネルを閉じる
}
```

`pgxpool.Pool.Close()` は同期的に全接続を即座に閉じる（drain ではない）。
dialer は Pool の後に安全に閉じられる。

---

## 優先度サマリー

| 優先度 | 課題 | 影響 |
|--------|------|------|
| CRITICAL | shutdown.Shutdown() にタイムアウトなし | closer ハング時にプロセスが無期限停止、SIGKILL |
| HIGH | CronJob ループが SIGTERM で即中断しない | 無駄な API 呼び出し3回 |
| HIGH | HealthServer.Close() にタイムアウトなし | ハング可能性 |
| HIGH | Router 二重 Close（安全だがノイジー） | ログノイズ |
| MEDIUM | Init() 二重呼び出しガードなし | テスト時のサイレント不整合 |
| MEDIUM | Init() 前 Shutdown() で nil panic | 初期化順序ミスでクラッシュ |
| LOW | Reset() スレッドセーフでない | 現時点で問題なし |

---

## 推奨アクション

### 最優先: タイムアウト予算の導入

1. 全エントリポイントで `shutdown.Shutdown(ctx)` に deadline 付き context を渡す
2. `HealthServer.Close()` に固定タイムアウト（5s）を追加
3. CronJob ループ先頭に `ctx.Err()` チェックを追加

### 次優先: 防御的コーディング

4. `Init()` に `sync.Once` ガードを追加
5. `run()` 先頭に nil logger チェックを追加

### 後回し可

6. Router の二重 Close はそのまま許容（idempotent であるため）
7. Reset() のスレッドセーフ化は parallel テスト導入時に対応
