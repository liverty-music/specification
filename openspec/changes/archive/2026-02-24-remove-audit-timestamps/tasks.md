## 1. Proto 層

- [x] 1.1 `user.proto` から `create_time` フィールド (field 3) を削除し、`reserved 3;` を追加。`google/protobuf/timestamp.proto` の import が不要なら削除
- [x] 1.2 `buf build` / `buf lint` で Proto のビルド・リントが通ることを確認

## 2. Go Entity 層

- [x] 2.1 `entity/user.go` から `CreateTime`, `UpdateTime` フィールドを削除
- [x] 2.2 `entity/entry.go` の `Nullifier.UsedAt` を `Nullifier.UseTime` にリネーム

## 3. Go Mapper 層

- [x] 3.1 `adapter/rpc/mapper/user.go` から `CreateTime` → `timestamppb` 変換コードを削除。`timestamppb` import が不要なら削除

## 4. Go Repository 層

- [x] 4.1 `rdb/user_repo.go` の SELECT/INSERT クエリから `created_at`, `updated_at` カラム参照を除去
- [x] 4.2 `Nullifier.UsedAt` → `UseTime` リネームに伴う repo 内の参照を修正

## 5. Go テスト

- [x] 5.1 `User` 関連テストから `CreateTime`, `UpdateTime` のアサーション・参照を削除
- [x] 5.2 `Nullifier` 関連テストの `UsedAt` → `UseTime` リネーム修正
- [x] 5.3 `go build ./...` と `go test ./...` が通ることを確認

## 6. DB マイグレーション

- [x] 6.1 新規マイグレーションファイルを作成し、6 テーブルから `created_at` / `updated_at` を DROP
- [x] 6.2 `schema.sql` から該当カラム定義とコメントを削除
- [x] 6.3 `atlas migrate hash` でチェックサムを更新
