## Why

Infrastructure layer のテストが go-tester 基準に準拠しておらず、パッケージごとにスタイルがばらばらである。また、interface の `Possible errors` ドキュメントに漏れや実装との不一致があり、usecase layer が正しいエラーハンドリングを行う前提が崩れている。さらに一部の実装が `apperr` を使わず `fmt.Errorf` で返却しており、エラーコード体系が機能しない。`database/rdb` パッケージで先行して行ったテスト標準化を、残りの infrastructure パッケージに展開し、エラーハンドリングの不備も同時に修正する。

## What Changes

### テスト標準化 (go-tester 準拠)
- ホワイトボックステスト (`package foo`) → ブラックボックス (`package foo_test`) + `export_test.go` パターンへ移行 (6 ファイル)
- ループ変数 `tc` → `tt` へ統一 (2 ファイル)
- `wantErr bool` / `wantErr string` → `wantErr error` に型修正 (3 ファイル)
- 冗長なエラーチェック (`require.Error` + `assert.ErrorIs`) → `assert.ErrorIs` のみに簡素化 (6 ファイル)
- `t.Errorf` → `testify/assert` に統一 (2 ファイル)
- テーブル駆動テストへの構造化 (6 ファイル)
- `t.Parallel()` の追加 (独立テスト関数)

### エラーハンドリング修正
- `codes.DataLoss` の誤用を `codes.Internal` に修正 (JSON デコード失敗は "unrecoverable data loss" ではない) — 5 ファイル、12 箇所
- `fmt.Errorf` で返却している実装を `apperr.Wrap` / `apperr.New` に移行 — 3 パッケージ (`ticketsbt`, `zkp`, `merkle`)

### Interface ドキュメント整備
- `Possible errors` 未定義の interface にドキュメント追加 (6 interface)
- 実装と不一致の `Possible errors` を修正 (4 interface)

### テストカバレッジ拡充
- テスト未作成パッケージへのテスト新規追加 (`webpush/sender.go`)
- エラーパステストの追加 (`OfficialSiteResolver`, `LogoImageFetcher`, `lastfm` API error code mapping)

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `entity-test-coverage`: infrastructure layer テストの品質基準と error contract の検証観点を追加

## Impact

- **backend/internal/infrastructure/** 配下の全テストファイル (約 25 ファイル)
- **backend/internal/entity/** の interface ドキュメント (6 entity ファイル)
- **backend/internal/infrastructure/blockchain/ticketsbt/**, **zkp/**, **merkle/** の実装コード
- **backend/internal/infrastructure/music/**, **maps/google/**, **gcp/gemini/** のエラーコード修正
- テストの `wantErr` 期待値が `DataLoss` → `Internal` に変更される (4 テストファイル)
- 外部 API の振る舞いに変更なし。エラーコードの内部分類のみの修正
