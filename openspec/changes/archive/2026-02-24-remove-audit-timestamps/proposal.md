## Why

Proto, Go entity, DB schema の各レイヤーに `created_at` / `updated_at` 系のメタデータタイムスタンプが散在しているが、アプリケーションのビジネスロジックで使用されていない。監査ログは別途対応するため、これらを全て削除してスキーマを簡素化する。併せて `UsedAt` → `UseTime` へリネームし、Go entity の命名規則を `XxxTime` パターンに統一する。

## What Changes

- **BREAKING** Proto: `user.proto` の `create_time` フィールドを削除
- Go Entity: `User.CreateTime`, `User.UpdateTime` フィールドを削除
- Go Entity: `Nullifier.UsedAt` を `Nullifier.UseTime` にリネーム（命名一貫性）
- Go Mapper: `User` の `timestamppb` 変換コードを削除
- Go Repo: `user_repo.go` の SELECT/INSERT から `created_at`, `updated_at` カラム参照を除去
- DB: 6 テーブルから `created_at` / `updated_at` カラムを DROP
  - `users`, `events`, `venues`, `artist_official_site`, `followed_artists`, `notifications`
- DB: `schema.sql` から該当カラム定義を削除

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `user-account-sync`: `User` エンティティから `create_time` を削除。API レスポンスの変更。
- `database`: 6 テーブルからタイムスタンプカラムを DROP するマイグレーション追加。

## Impact

- **Proto/API**: `User` メッセージから `create_time` フィールドが消えるため、API クライアントに breaking change
- **Backend**: entity, mapper, repo, テストの修正
- **DB**: 新規マイグレーションファイルが必要（ALTER TABLE ... DROP COLUMN）
- **Frontend**: `create_time` を参照していないため影響なし
