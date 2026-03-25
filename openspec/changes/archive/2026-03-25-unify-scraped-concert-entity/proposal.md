## Why

`ScrapedConcert` (domain entity) と `ScrapedConcertData` (event DTO) は全フィールドが同一であり、EDA 導入時に後付けで生まれた偶発的な重複である。また、重複排除ロジックが usecase 層に直書きされており、ドメインルール（同一アーティストが同日に 2 公演ない）がテストしにくい状態になっている。この変更で冗長な型を廃止し、ドメインロジックをエンティティ層に移動することで責務を整理する。

## What Changes

- **BREAKING** `entity.ScrapedConcertData` 型を廃止し、`entity.ScrapedConcert` に JSON タグを追加して統合する
- `entity.ScrapedConcerts` コレクション型 (`type ScrapedConcerts []*ScrapedConcert`) を新規追加する
- `ScrapedConcerts.FilterNew(existing []*Concert) ScrapedConcerts` メソッドを追加する（既存コンサートと照合し新着のみ返す）
- `concert_uc.go` の重複排除ループを `ScrapedConcerts.FilterNew()` 呼び出しに置き換える
- `ConcertDiscoveredData.Concerts` の型を `[]ScrapedConcertData` → `[]ScrapedConcert` に変更する

## Capabilities

### New Capabilities

なし（既存の `entity-domain-logic` capability に要件を追加する）

### Modified Capabilities

- `entity-domain-logic`: `ScrapedConcerts` コレクション型と `FilterNew` メソッドの要件を追加する

## Impact

- `backend/internal/entity/concert.go`: `ScrapedConcerts` 型と `FilterNew` メソッドを追加、`ScrapedConcert` に JSON タグを追加
- `backend/internal/entity/event_data.go`: `ScrapedConcertData` 型を削除、`ConcertDiscoveredData.Concerts` の型を変更
- `backend/internal/usecase/concert_uc.go`: 重複排除ループを `FilterNew()` 呼び出しに置き換え
- `backend/internal/usecase/concert_creation_uc.go`: `ScrapedConcertData` 参照を `ScrapedConcert` に変更
- `backend/internal/entity/concert_test.go`: `FilterNew` のテストを追加
