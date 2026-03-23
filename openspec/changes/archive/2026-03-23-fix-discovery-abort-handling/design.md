## Context

DiscoveryRoute で `searchConcertsForArtist()` は fire-and-forget パターンで呼ばれる。現在 `AbortController.signal` を RPC に渡しており、`detaching()` で `abort()` が呼ばれるとリクエストがキャンセルされる。

サーバー側は意図的に Gemini API 呼び出しをキャンセルしない設計（Gemini の検索結果を無駄にしないため）。フロントエンドがリクエストをキャンセルしてもサーバーは処理を続行するため、abort は無意味かつノイズの原因になっている。

## Goals / Non-Goals

**Goals:**
- ページ遷移時に `SearchNewConcerts` RPC をキャンセルしない
- ページ遷移後の RPC 完了時、データ更新は実行するが UI 通知（Snack）はスキップする
- AbortError / ConnectError(Canceled) を transport interceptor で error ログから除外する

**Non-Goals:**
- サーバー側の変更
- AbortController 自体の削除（他の UI ガードで引き続き使用）
- Gemini invalid JSON エラーの修正（別 change で対応）

## Decisions

### 1. `searchConcertsForArtist()` から signal を除去

`discovery-route.ts` の `searchConcertsForArtist()` で `this.abortController.signal` を渡さないようにする。

呼び出しチェーン全体:
```
discovery-route.ts  →  concert-service.ts  →  concert-client.ts  →  Connect transport
  (signal除去)         (signal?: optional)     (signal?: optional)    (signalなし)
```

`concert-service.ts` と `concert-client.ts` の `signal?` パラメータはオプショナルなので、呼び出し側で渡さなければそのまま `undefined` として伝播する。変更は `discovery-route.ts` のみで済む。

detach 後の振る舞い:
- `addArtistWithConcerts()` → 実行する（データ整合性のため）
- `ea.publish(new Snack(...))` → `abortController.signal.aborted` チェックでスキップ（既存のL308ガードがそのまま使える）

### 2. transport interceptor の AbortError 除外

`grpc-transport.ts` の2つの interceptor を修正:

**loggingInterceptor:**
- AbortError (`err.name === 'AbortError'`) → ログ出力しない（re-throw のみ）
- ConnectError で code が `Canceled` → ログ出力しない
- その他 → 現状通り `logger.error`

**otelInterceptor:**
- AbortError → `SpanStatusCode.OK` で終了（キャンセルは正常終了）
- ConnectError(Canceled) → `SpanStatusCode.OK` で終了
- その他 → 現状通り `SpanStatusCode.ERROR`

理由: AbortError は `ConnectError` ではなく `DOMException` としてスローされるため、`instanceof ConnectError` の分岐には入らない。明示的に `err.name === 'AbortError'` でチェックする必要がある。

## Risks / Trade-offs

- **[Risk] RPC 完了後に unmount 済みコンポーネントの状態を更新する** → `addArtistWithConcerts` は singleton service のメソッドなのでコンポーネントのライフサイクルに依存しない。Snack は EventAggregator 経由で app-level のため問題なし。ただし `aborted` チェックでスキップするので Snack は表示されない
- **[Risk] signal を渡さないことで、長時間ハングするリクエストをユーザーが止められない** → `SearchNewConcerts` はサーバー側でタイムアウト管理されており、クライアント側での中断は不要
