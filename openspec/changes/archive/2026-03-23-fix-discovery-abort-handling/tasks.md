## 1. DiscoveryRoute — signal 除去

- [x] 1.1 `discovery-route.ts` の `searchConcertsForArtist()` で `this.abortController.signal` を RPC に渡さないよう変更
- [x] 1.2 detach 後ガード: `abortController.signal.aborted` 時は `addArtistWithConcerts()` は実行し、Snack 表示のみスキップするよう調整
- [x] 1.3 既存テスト `discovery-route.spec.ts` を更新（signal が渡されないことを反映）

## 2. Transport interceptor — AbortError ログ抑制

- [x] 2.1 `grpc-transport.ts` の `loggingInterceptor` で AbortError と ConnectError(Canceled) をログ出力しないよう分岐追加
- [x] 2.2 `grpc-transport.ts` の `otelInterceptor` で AbortError と ConnectError(Canceled) を `SpanStatusCode.OK` で終了するよう変更

## 3. 検証

- [x] 3.1 `make check` (lint + test) パス確認
