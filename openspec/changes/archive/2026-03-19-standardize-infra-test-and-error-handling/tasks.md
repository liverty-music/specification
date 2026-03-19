## 1. エラーコード修正 (DataLoss → Internal)

- [x] 1.1 `music/fanarttv/client.go`: `codes.DataLoss` → `codes.Internal` (2 箇所: response body read, JSON decode)
- [x] 1.2 `music/lastfm/client.go`: `codes.DataLoss` → `codes.Internal` (2 箇所: response body read, JSON decode)
- [x] 1.3 `maps/google/client.go`: `codes.DataLoss` → `codes.Internal` (1 箇所: JSON decode)
- [x] 1.4 `music/musicbrainz/client.go`: `codes.DataLoss` → `codes.Internal` (3 箇所: artist/url-rels/place decode)
- [x] 1.5 テストの `wantErr` 期待値を更新: `codes.DataLoss` → `codes.Internal` (fanarttv, lastfm, google, musicbrainz の各 client_test.go)

## 2. apperr 未使用の実装を修正

- [x] 2.1 `blockchain/ticketsbt/client.go`: `fmt.Errorf` → `apperr.Wrap(err, codes.Internal, ...)` に移行
- [x] 2.2 `zkp/verifier.go`: `fmt.Errorf` → `apperr.Wrap(err, codes.Internal, ...)` に移行
- [x] 2.3 `merkle/tree.go`: `fmt.Errorf` → `apperr.New(codes.InvalidArgument, ...)` (too many leaves) + `apperr.Wrap(err, codes.Internal, ...)` (hash 失敗) に移行

## 3. Interface Possible errors ドキュメント追加

- [x] 3.1 `entity/entry.go`: NullifierRepository の全メソッドに `# Possible errors` 追加 (InvalidArgument, AlreadyExists, Internal)
- [x] 3.2 `entity/entry.go`: MerkleTreeRepository の全メソッドに `# Possible errors` 追加 (InvalidArgument, NotFound, Internal)
- [x] 3.3 `entity/entry.go`: EventRepository (GetMerkleRoot, UpdateMerkleRoot, GetTicketLeafIndex) に `# Possible errors` 追加 (InvalidArgument, NotFound, Internal)
- [x] 3.4 `entity/ticket.go`: TicketMinter の全メソッドに `# Possible errors` 追加 (Internal)
- [x] 3.5 `entity/entry.go`: ZKPVerifier に `# Possible errors` 追加 (Internal)
- [x] 3.6 `entity/merkle.go`: MerkleTreeBuilder の全メソッドに `# Possible errors` 追加 (InvalidArgument, Internal)

## 4. Interface Possible errors 不一致修正

- [x] 4.1 `entity/ticket_email_parser.go`: TicketEmailParser に `InvalidArgument` 追加 (未サポート email type)
- [x] 4.2 `entity/fanart.go`: LogoImageFetcher に `InvalidArgument` 追加 (URL 検証)
- [x] 4.3 `entity/artist.go`: ArtistSearcher のドキュメント見直し — Last.fm API error code mapping で返る NotFound 等を反映
- [x] 4.4 `entity/concert.go`: ConcertSearcher のドキュメント見直し — toAppErr 経由の Internal 等を反映

## 5. テスト標準化 — ホワイトボックス→ブラックボックス

- [x] 5.1 `auth/jwt_validator_test.go`: `package auth` → `package auth_test` + 必要に応じて `export_test.go` 作成
- [x] 5.2 `auth/context_test.go`: `package auth` → `package auth_test` + `export_test.go` で context key を公開
- [x] 5.3 `blockchain/safe/address_test.go`: `package safe` → `package safe_test`
- [x] 5.4 `server/cors_test.go`: `package server` → `package server_test`
- [x] 5.5 `merkle/tree_test.go`: `package merkle` → `package merkle_test`
- [x] 5.6 `music/fanarttv/logo_fetcher_test.go`: `package fanarttv` → `package fanarttv_test` + `export_test.go` で `validateLogoURL` を公開

## 6. テスト標準化 — 構造・命名・アサーション

- [x] 6.1 `blockchain/ticketsbt/client_test.go`: ループ変数 `tc` → `tt`、`wantErr string` → `wantErr error`
- [x] 6.2 `zkp/verifier_test.go`: ループ変数 `tc` → `tt`、`expectErr bool` → `wantErr error`
- [x] 6.3 `music/fanarttv/logo_fetcher_test.go`: `wantErr bool` → `wantErr error`
- [x] 6.4 `blockchain/safe/address_test.go`: `t.Errorf` → `assert.*` に統一 + テーブル駆動化
- [x] 6.5 `auth/context_test.go`: `t.Errorf` / `if` チェック → `assert.*` に統一
- [x] 6.6 冗長エラーチェック除去: `music/musicbrainz/client_test.go`, `music/lastfm/client_test.go`, `gcp/gemini/searcher_test.go` から `assert.Error` + `assert.ErrorIs` → `assert.ErrorIs` のみ

## 7. テスト標準化 — テーブル駆動化

- [x] 7.1 `auth/authn_test.go`: 個別テスト関数 → テーブル駆動テストに統合
- [x] 7.2 `auth/jwt_validator_test.go`: `TestValidateToken` サブテスト → テーブル駆動化
- [x] 7.3 `server/cors_test.go`: テーブル駆動テスト化
- [x] 7.4 `merkle/tree_test.go`: `t.Run` サブテスト → テーブル駆動化
- [x] 7.5 `music/fanarttv/client_test.go`: 個別 `t.Run` → テーブル駆動化

## 8. テストカバレッジ拡充 — エラーパス

- [x] 8.1 `webpush/sender_test.go` 新規作成: NotFound (HTTP 410 Gone), Internal パスのテスト
- [x] 8.2 `music/musicbrainz/client_test.go`: OfficialSiteResolver (`ResolveOfficialSiteURL`) のエラーパステスト追加
- [x] 8.3 `music/fanarttv/logo_fetcher_test.go`: URL 検証エラーの `wantErr` を具体的な `apperr` コードでチェック + 404→nil テスト追加
- [x] 8.4 `music/lastfm/client_test.go`: Last.fm API error code mapping (codes 6, 4, 9, 10, 14, 15, 29) のテスト追加

## 9. t.Parallel() 追加

- [x] 9.1 `gcp/gemini/searcher_test.go`, `retry_test.go`: 独立テスト関数に `t.Parallel()` 追加
- [x] 9.2 `maps/google/client_test.go`, `place_searcher_test.go`: `t.Parallel()` 追加
- [x] 9.3 `music/musicbrainz/client_test.go`, `place_searcher_test.go`: `t.Parallel()` 追加
- [x] 9.4 `music/lastfm/client_test.go`: `t.Parallel()` 追加
- [x] 9.5 `music/fanarttv/client_test.go`: `t.Parallel()` 追加

## 10. 検証

- [x] 10.1 `go build ./internal/infrastructure/...` でコンパイル確認
- [x] 10.2 `go test ./internal/infrastructure/...` で全テスト通過確認
