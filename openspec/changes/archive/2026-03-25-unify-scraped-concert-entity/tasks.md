## 1. Entity 層: ScrapedConcert の統合

- [x] 1.1 `entity.ScrapedConcert` の全フィールドに JSON タグを追加する（`title`, `listed_venue_name`, `admin_area,omitempty`, `local_date`, `start_time,omitempty`, `open_time,omitempty`, `source_url`）
- [x] 1.2 `type ScrapedConcerts []*ScrapedConcert` を `concert.go` に追加する
- [x] 1.3 `ScrapedConcerts.FilterNew(existing []*Concert) ScrapedConcerts` メソッドを実装する（date-only dedup、バッチ内 dedup も含む）

## 2. Entity 層: テスト

- [x] 2.1 `concert_test.go` に `TestScrapedConcerts_FilterNew` を追加し、以下のシナリオをカバーする:
  - 空の scraped リスト → nil を返す
  - existing が空 → 全 scraped を返す
  - 全件が existing と衝突 → nil を返す
  - 部分一致（3件中1件が衝突） → 2件を元の順序で返す
  - バッチ内同日重複（existing なし） → 最初の1件のみ返す
  - バッチ内同日重複 + existing も同日 → nil を返す
  - 順序の保持（Mar15, Mar17, Mar16 の順を維持）
  - existing が nil → 全 scraped を返す
- [x] 2.2 `ScrapedConcert` の JSON シリアライズテストを追加する:
  - nil optional フィールドが JSON 出力から省略されること
  - 全フィールドが正しいキー名でシリアライズされること

## 3. Entity 層: ScrapedConcertData の廃止

- [x] 3.1 `entity/event_data.go` の `ScrapedConcertData` 型を削除する
- [x] 3.2 `entity.ConcertDiscoveredData.Concerts` の型を `ScrapedConcerts` に変更する

## 4. UseCase 層: concert_uc.go のリファクタリング

- [x] 4.1 `concert_uc.go` の `executeSearch` 内の dedup ループ（`seenDate` マップ構築 + `newScraped` への変換）を `ScrapedConcerts(scraped).FilterNew(existing)` 呼び出しに置き換える
- [x] 4.2 `newScraped` の型を `entity.ScrapedConcerts` に変更する
- [x] 4.3 `ConcertDiscoveredData` 生成時の `Concerts` フィールドへの代入を確認・修正する

## 5. UseCase 層: concert_creation_uc.go の修正

- [x] 5.1 `concert_creation_uc.go` 内の `ScrapedConcertData` 参照をすべて `ScrapedConcert` に変更する
- [x] 5.2 `ScrapedConcertData` のフィールドアクセスが `ScrapedConcert` でも同一であることを確認する（フィールド名は変わらないため差分なし）

## 6. 最終確認

- [x] 6.1 `make lint` を実行してコンパイルエラー・lint エラーがないことを確認する
- [x] 6.2 `make test` を実行してすべてのテストが通ることを確認する
