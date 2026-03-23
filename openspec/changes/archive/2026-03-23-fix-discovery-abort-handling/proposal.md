## Why

DiscoveryRoute からページ遷移すると、進行中の `SearchNewConcerts` RPC が `AbortController.abort()` でキャンセルされ、コンソールに `[ERR Transport] RPC error AbortError: signal is aborted without reason` が複数件表示される。サーバー側では意図的に Gemini API 呼び出しをキャンセルしないため、フロントエンドもキャンセルしないよう合わせる必要がある。また、AbortError が `logger.error` レベルで出力されており、本当のエラーとの区別がつきにくい。

## What Changes

- **DiscoveryRoute**: `searchConcertsForArtist()` で AbortSignal を RPC に渡さないよう変更。ページ遷移後もリクエストは完走するが、UI 更新（Snack 表示）はスキップする
- **grpc-transport**: `loggingInterceptor` と `otelInterceptor` で AbortError / ConnectError(Canceled) を error レベルから除外し、デバッグログまたはスキップに変更

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. Implementation-level の変更のみで、仕様レベルの要件変更はなし。

## Impact

- **frontend** `src/routes/discovery/discovery-route.ts` — signal 引数の除去、detach 後の UI ガード調整
- **frontend** `src/services/grpc-transport.ts` — interceptor のエラー分岐追加
- ユーザー影響: コンソールノイズの削減。機能的な変更なし
