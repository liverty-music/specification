## Context

Proto, Go entity, DB schema の各レイヤーに `created_at` / `updated_at` メタデータタイムスタンプが存在するが、ビジネスロジックでは使用されていない。`artists` と `concerts` テーブルは既に migration `20260221130000` で削除済み。残り 6 テーブルと Proto/Go 層の整理が必要。

併せて `Nullifier.UsedAt` の命名が他の `XxxTime` パターンと不一致のため修正する。

## Goals / Non-Goals

**Goals:**
- 全テーブルから `created_at` / `updated_at` メタデータカラムを削除
- `user.proto` から `create_time` フィールドを削除
- Go entity / mapper / repo から関連コードを削除
- `Nullifier.UsedAt` → `UseTime` にリネーム
- テストの関連アサーションを修正

**Non-Goals:**
- ビジネスタイムスタンプ (`minted_at`, `start_at`, `open_at`, `searched_at`, `scheduled_at`, `sent_at`, `used_at`) には触れない
- 監査ログの代替実装（別途対応）
- DB カラム `used_at` のリネーム（DB 層は `_at` が慣習、Go 層のみ修正）

## Decisions

### 1. Proto フィールド番号を reserved にする

`user.proto` から `create_time` (field number 3) を削除した後、将来の誤用を防ぐため `reserved 3;` を追加する。

**理由**: Proto のフィールド番号再利用は wire format の互換性を壊すため、Google AIP のベストプラクティスに従う。

### 2. マイグレーションは 1 ファイルで全テーブルをまとめる

6 テーブルの `DROP COLUMN` を 1 つのマイグレーションファイルにまとめる。

**理由**: 全て同じ理由（メタデータタイムスタンプ削除）であり、原子的に適用すべき。既存の `20260221130000_drop_artists_timestamps.sql` と同じパターン。

### 3. Go entity の `UsedAt` → `UseTime` リネームは DB カラム名を変えない

Go struct フィールド名のみ変更し、DB カラム `used_at` はそのまま。repo のスキャン先を調整する。

**理由**: DB カラムは `_at` サフィックスが PostgreSQL の慣習。Go 側のみ `XxxTime` パターンに統一する。

## Risks / Trade-offs

- **[Breaking API Change]** `User.create_time` を削除するため、既存 API クライアントに影響 → 現在フロントエンドでは未使用を確認済み。Proto の `reserved` で将来の誤用を防止。
- **[DB Migration]** `DROP COLUMN` は PostgreSQL ではメタデータ操作のみでテーブルリライトは発生しない → リスク低い。ただし `DEFAULT NOW()` のトリガーがある場合は確認が必要。
