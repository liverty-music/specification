## Context

現在、コンサートスクレイピングパイプラインには2つの構造体が存在する：

- `entity.ScrapedConcert` — Gemini からパースした生データを表すドメインエンティティ
- `entity.ScrapedConcertData` — `concert.discovered` イベントのペイロード用 DTO

両者のフィールドは完全に一致しており、唯一の違いは JSON タグの有無のみ。EDA 導入（2026-03-06）時に `messaging` パッケージに追加され、`refactor-usecase-layer-boundaries`（2026-03-12）で `entity` パッケージに移動したが、統合はされなかった。

また、重複排除ロジック（同一アーティストが同日に 2 公演ない）は `concert_uc.go` の `executeSearch` に直書きされており、ドメインルールとしてのテスト独立性がない。

## Goals / Non-Goals

**Goals:**
- `ScrapedConcertData` を廃止し `ScrapedConcert` に統合することで型の重複を解消する
- 重複排除ロジックを `entity.ScrapedConcerts.FilterNew()` として entity 層に移動する
- `FilterNew` の単体テストを entity 層で書けるようにする

**Non-Goals:**
- スクレイピングパイプライン自体の変更
- `concert.discovered` イベントスキーマの変更（フィールド名・内容は同一）
- Protobuf 定義の変更（`ScrapedConcert` は内部型であり proto には存在しない）

## Decisions

### Decision 1: `ScrapedConcert` に JSON タグを追加して `ScrapedConcertData` を廃止

**選択**: `ScrapedConcert` に JSON タグを付与し、`ScrapedConcertData` を削除する。

**代替案**: `ScrapedConcertData` を正として `ScrapedConcert` を廃止し `ScrapedConcertData` にメソッドを追加する。

**理由**: `ScrapedConcert` がメソッド（`DateKey()`）を持つ「振る舞いを持つエンティティ」であり、ドメインモデルとして先に存在した型。イベントペイロード用 DTO が後付けで生まれた経緯から、主として `ScrapedConcert` を残すのが自然。また、`entity` パッケージの規約上 JSON タグは "unless necessary" の例外として認められており、今回はイベント通信という必然的ユースケースがある。

### Decision 2: コレクション型 `ScrapedConcerts` を定義して `FilterNew` をメソッドとして実装

**選択**: `type ScrapedConcerts []*ScrapedConcert` を定義し、`FilterNew(existing []*Concert) ScrapedConcerts` メソッドを付与する。

**代替案A**: パッケージレベル関数 `FilterNewConcerts(scraped []*ScrapedConcert, existing []*Concert) []*ScrapedConcert` として定義する。

**代替案B**: `ScrapedConcert` に個別メソッドを追加し、usecase 側でループする。

**理由**: コレクション型にすることで「スライスに対する操作」という意図が型から明確になる。また `GroupByDateAndProximity` のような関数と一貫したパターンを踏まえると、コレクション型のメソッドが最も自然。将来的に `Concerts` フィールドの型を `ScrapedConcerts` に変更すれば呼び出し側もシンプルになる。

### Decision 3: `FilterNew` の dedup キーは date-only（`DateKey()`）を使用

**選択**: `LocalDate.Format("2006-01-02")` による日付単位の重複排除を維持する。

**理由**: `concert_uc.go` の既存ロジックと一致。仕様（`concert-search/spec.md`）でも "one event per artist per date" と定義されており、entity 層に移してもこのセマンティクスは変わらない。`DedupeKey()` は venue/start_time を含むより厳密なキーだが、現行の排除ルールは date-only であり、それを維持する。

## Risks / Trade-offs

- **`ScrapedConcert` に JSON タグが入ることで entity の "pure struct" 原則と若干競合する** → AGENTS.md の "no tags (unless necessary)" という注釈がこの例外を許容している。イベント通信という必然的ユースケースであり、Proto 型ではない内部型であるため許容範囲内と判断する。
- **バッチ内重複排除（同一バッチ内に同日コンサートが複数ある場合）も `FilterNew` 内で処理される** → `seenDate` マップを `FilterNew` 内に持つことでバッチ内 dedup と既存 dedup を統一して処理できる。usecase 側の責務がシンプルになる。

## Migration Plan

1. `entity.ScrapedConcert` に JSON タグを追加
2. `entity.ScrapedConcerts` 型と `FilterNew` メソッドを追加（テスト含む）
3. `entity.ScrapedConcertData` を削除し、`ConcertDiscoveredData.Concerts` の型を `[]ScrapedConcert` に変更
4. `concert_uc.go` の dedup ループを `ScrapedConcerts(scraped).FilterNew(existing)` に置き換え
5. `concert_creation_uc.go` の `ScrapedConcertData` 参照を `ScrapedConcert` に変更
6. コンパイル確認・全テスト通過を確認

ロールバック: 1 PR に収まる変更であり、revert で即時ロールバック可能。イベントスキーマのフィールド名は変わらないため、`concert.discovered` コンシューマへの影響なし。

## Open Questions

なし
