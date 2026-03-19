## Context

`database/rdb` パッケージでテスト標準化を先行実施済み。その過程で確立したパターン:
- ブラックボックステスト (`package rdb_test`)
- ループ変数 `tt`、`wantErr error` 型
- 冗長な `require.Error` + `assert.ErrorIs` → `assert.ErrorIs` のみ
- shared seed helpers (`setup_test.go`)

残りの infrastructure パッケージ (auth, blockchain, gcp/gemini, maps/google, music/*, server, geo, zkp, merkle) にはこれらの基準への準拠が不十分な箇所がある。

同時に、interface の `Possible errors` ドキュメントと実装の整合性調査で以下を発見:
1. 6 interface に `Possible errors` が未定義
2. 3 パッケージが `apperr` を使わず `fmt.Errorf` で返却
3. 全外部 API クライアントが JSON デコード失敗を `codes.DataLoss` で返しているが、これは gRPC 定義の "unrecoverable data loss" とは異なる

## Goals / Non-Goals

**Goals:**
- go-tester スキル基準への全 infrastructure テストの準拠
- 全 interface の `Possible errors` ドキュメントの完備
- 実装が返すエラーコードと interface ドキュメントの一致保証
- `apperr` 未使用の実装を修正し、エラーコード体系を統一
- `codes.DataLoss` の誤用を `codes.Internal` に修正

**Non-Goals:**
- テストカバレッジ 100% の達成 (テストなしの `messaging/` パッケージは対象外)
- `Unavailable` と `Internal` の統合 (ログの可観測性で区別の価値がある)
- テスト構造以外のリファクタリング (実装ロジックの変更は最小限)

## Decisions

### 1. `DataLoss` → `Internal` への変更

**決定**: JSON デコード失敗時のエラーコードを `codes.DataLoss` から `codes.Internal` に変更する。

**理由**: gRPC の `DataLoss` は "Unrecoverable data loss or corruption" を意味する。外部 API レスポンスの JSON デコード失敗は「想定外のレスポンス形式」であり、データ損失ではない。`Internal` ("Internal errors — unexpected conditions") が適切。

**影響範囲**: 5 実装ファイル (fanarttv/client.go, lastfm/client.go, google/client.go, musicbrainz/client.go x3箇所) + 4 テストファイルの `wantErr` 期待値。

### 2. `fmt.Errorf` → `apperr` への移行方針

**決定**: `ticketsbt`, `zkp`, `merkle` の 3 パッケージで `fmt.Errorf` → `apperr.Wrap` / `apperr.New` に移行する。

**理由**: usecase layer が `apperr.Code(err)` でエラーを分類するため、apperr 以外のエラーは `Unknown` として扱われ、適切なハンドリングができない。

**エラーコードの割り当て**:

| パッケージ | エラー状況 | コード |
|-----------|----------|--------|
| ticketsbt | RPC 失敗、トランザクション失敗 | `Internal` |
| zkp | JSON パース失敗、変換失敗 | `Internal` |
| merkle | Poseidon hash 失敗 | `Internal` |
| merkle | "too many leaves" (入力超過) | `InvalidArgument` |

### 3. ホワイトボックス→ブラックボックスの移行手順

**決定**: 未エクスポートシンボルへのアクセスが必要な場合のみ `export_test.go` を作成。不要な場合はパッケージ名の `_test` 付与のみ。

**対象ファイルの分析**:

| ファイル | 未エクスポートシンボルへのアクセス | 対応 |
|---------|-------------------------------|------|
| auth/jwt_validator_test.go | `setupTestJWKS` 内で未エクスポート構造体使用の可能性 | 要調査 → `export_test.go` が必要なら作成 |
| auth/context_test.go | `claimsKey`, `userIDKey` (未エクスポート context key) | `export_test.go` で公開 |
| safe/address_test.go | なし (exported `PredictAddress` のみ) | パッケージ名変更のみ |
| server/cors_test.go | なし (exported `GetCorsOptions` のみ) | パッケージ名変更のみ |
| merkle/tree_test.go | なし (exported `Build`, `IdentityCommitment` のみ) | パッケージ名変更のみ |
| fanarttv/logo_fetcher_test.go | `validateLogoURL` (未エクスポート関数) | `export_test.go` で公開 |

### 4. テスト新規作成の範囲

**決定**: `webpush/sender.go` のテストを新規作成する。`messaging/` パッケージは対象外。

**理由**: `webpush/sender.go` は interface (`PushNotificationSender`) の直接実装であり、`Possible errors` (NotFound, Internal) のテストが必要。`messaging/` は pub/sub 基盤でありテスト設計が複雑で、別変更として扱うべき。

## Risks / Trade-offs

**[Risk] `export_test.go` 作成時に未エクスポートシンボルの依存関係を見落とす**
→ Mitigation: 各ファイルをブラックボックスに変更後、コンパイルエラーで即座に検出。`go build ./...` で確認。

**[Risk] `DataLoss` → `Internal` 変更でログの分類粒度が下がる**
→ Mitigation: エラーメッセージ文字列は変更しないため、ログ検索では引き続き "failed to decode" で特定可能。コード分類の正確性を優先する。

**[Risk] `ticketsbt` の `fmt.Errorf` → `apperr` 移行で既存の error wrapping chain が壊れる**
→ Mitigation: `apperr.Wrap` は元エラーを保持するため、`errors.Is` / `errors.As` の既存チェックは引き続き動作する。
