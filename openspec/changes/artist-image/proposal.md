## Why

Artist のカード表示（my-artists ページ、dashboard コンサートカード）やロゴ表示（dashboard）に画像がない。現在は名前ハッシュによる HSL カラーのみで視覚的識別を行っているが、ファンが直感的にアーティストを認識できる画像・ロゴが必要。fanart.tv API が MusicBrainz ID ベースでアーティスト画像を提供しており、既存の MBID 資産を活用できる。

## What Changes

- Artist エンティティに fanart.tv から取得した画像データ（Fanart）を追加
- fanart.tv API クライアントを backend に実装（既存の Last.fm / MusicBrainz クライアントと同パターン）
- `ARTIST.created` イベントで非同期に画像を即時取得（onboarding 時の dashboard ロゴ表示に必要）
- 定期 CronJob (`artist-image-sync`) で画像データの更新とバックフィルを実施
- Proto の Artist メッセージに Fanart メッセージを追加し、mapper で best image（likes 最大）を選択して返却
- DB の artists テーブルに `fanart` (JSONB) と `fanart_synced_at` (TIMESTAMPTZ) カラムを追加
- Proto の `SourceUrl`, `FanartImageUrl`, `OfficialSiteUrl` を汎用 `Url` メッセージに統合

## Capabilities

### New Capabilities

- `artist-image`: fanart.tv からアーティスト画像（thumb, background, logo, banner）を取得・保存・配信する仕組み

### Modified Capabilities

- `artist-service-infrastructure`: Artist エンティティへの Fanart フィールド追加、ArtistRepository への UpdateFanart 操作追加

## Impact

- **Proto**: `liverty_music.entity.v1.Artist` に `Fanart` メッセージ追加 + `SourceUrl`/`FanartImageUrl`/`OfficialSiteUrl` → `Url` 統合（ソース破壊・ワイヤ互換変更、`buf skip breaking` ラベル必要）
- **Backend**: entity, usecase, adapter/event, adapter/rpc/mapper, infrastructure/music/fanarttv, infrastructure/database/rdb, cmd/job, di 各レイヤーに変更
- **DB**: artists テーブルへのカラム追加マイグレーション
- **K8s**: artist-image-sync CronJob マニフェスト追加、FANARTTV_API_KEY の Secret/ConfigMap 管理
- **Frontend**: スコープ外（別 change で対応）
