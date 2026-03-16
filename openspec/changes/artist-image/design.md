## Context

Artist エンティティには画像情報がなく、フロントエンドでは名前ハッシュの HSL カラーのみで識別している。fanart.tv はコミュニティ駆動のアーティスト画像データベースで、MusicBrainz ID (MBID) をキーにアーティスト画像（thumb, background, logo, banner）を無料 API で提供している。

既存の backend には以下の基盤がある:
- `ARTIST.created` イベント（Watermill + NATS JetStream）
- Last.fm / MusicBrainz クライアント（throttle + retry パターン）
- concert-discovery CronJob（circuit breaker パターン）
- ArtistNameConsumer（イベント駆動の非同期処理パターン）

## Goals / Non-Goals

**Goals:**
- fanart.tv API から MBID ベースでアーティスト画像データを取得し DB に保存する
- `ARTIST.created` イベントで即時取得（onboarding 時の dashboard ロゴ表示）
- 定期 CronJob で画像データの更新とバックフィルを実施
- Proto の Artist メッセージに Fanart を含め、RPC で best image を返却する

**Non-Goals:**
- フロントエンド側の画像表示実装（別 change）
- 画像ファイルのダウンロード・自前ホスティング（fanart.tv URL を直接使用）
- fanart.tv 以外の画像ソースへの抽象化

## Decisions

### 1. DB ストレージ: JSONB 単一カラム

fanart.tv API レスポンスを `fanart` JSONB カラムにそのまま保存する。

```sql
ALTER TABLE artists
    ADD COLUMN fanart JSONB,
    ADD COLUMN fanart_synced_at TIMESTAMPTZ;
```

**Why**: fanart.tv のレスポンスは「外部キャッシュ」の性質。正規化テーブルに分解すると定期更新時の diff/upsert が複雑になる。JSONB なら丸ごと上書きで済む。画像選択ロジック（likes 最大）は Go 側で処理する。

**Alternatives considered**:
- `artist_images` 正規化テーブル: 1 アーティストで 10+ 行になりうる。定期更新時の diff が複雑。画像タイプ追加のたびにスキーマ対応が必要。
- 画像タイプ別カラム (`thumb_url`, `logo_url`): best image 選択が DB 側に固定される。全候補データが失われる。

### 2. Entity 設計: fanart.tv 構造をそのままドメインに出す

fanart.tv を抽象化せず、ビジネスロジックの一部として扱う。Entity のフィールド構成は fanart.tv レスポンスと同一にする。

```go
type Fanart struct {
    ArtistThumb      []FanartImage `json:"artistthumb"`
    ArtistBackground []FanartImage `json:"artistbackground"`
    HDMusicLogo      []FanartImage `json:"hdmusiclogo"`
    MusicLogo        []FanartImage `json:"musiclogo"`
    MusicBanner      []FanartImage `json:"musicbanner"`
}

type FanartImage struct {
    ID    string `json:"id"`
    URL   string `json:"url"`
    Likes int    `json:"likes,string"`
    Lang  string `json:"lang"`
}
```

`Artist` struct に `Fanart *Fanart` と `FanartSyncTime *time.Time` を追加。

**Why**: JSONB ↔ Go struct の変換が `json.Unmarshal` 一発で済む。fanart.tv の新しい画像タイプが追加された場合も struct にフィールドを足すだけ。

### 3. Proto: Fanart メッセージで best image を返す

Proto では各画像タイプに対して best image（likes 最大）の URL を 1 つだけ返す。

```protobuf
message Fanart {
    optional Url artist_thumb = 1;
    optional Url artist_background = 2;
    optional Url hd_music_logo = 3;
    optional Url music_logo = 4;
    optional Url music_banner = 5;
}

message Artist {
    ...
    optional Fanart fanart = 4;
}
```

**Why**: フロントエンドに全候補リストを返す必要はない。best image 選択はバックエンドの責務。ロゴのフォールバック（`hd_music_logo ?? music_logo`）はフロントエンド側で行う。

### 4. 取得タイミング: Event Consumer + CronJob のハイブリッド

| 仕組み | トリガー | 目的 |
|--------|---------|------|
| `ArtistImageConsumer` | `ARTIST.created` イベント | 即時取得（onboarding dashboard） |
| `artist-image-sync` CronJob | 日次スケジュール | 定期更新 + バックフィル |

両者は同じ `ArtistImageSyncUseCase` と fanart.tv クライアントを共有する。

**Why**: onboarding フローで Artist フォロー直後に dashboard でロゴを表示する必要がある。CronJob だけでは最大 24h の遅延が発生する。

### 5. fanart.tv クライアント: 既存パターン踏襲

Last.fm クライアントと同じアーキテクチャで実装。

- `infrastructure/music/fanarttv/client.go`
- `throttle.Throttler` でレートリミット制御
- `backoff.Retry` でリトライ（exponential backoff, max 4 tries）
- `httpx.IsRetryableStatus` で 429/503/504 をリトライ対象に
- API key は環境変数 `FANARTTV_API_KEY` から取得
- `entity.ArtistImageResolver` インターフェースを実装

### 6. Best Image 選択: likes 最大

```go
func BestByLikes(images []FanartImage) string {
    // likes が最大の画像 URL を返す。空スライスなら空文字列。
}
```

Entity のメソッドとして定義し、mapper 層から呼び出す。

### 7. CronJob 設計: concert-discovery と同パターン

- `cmd/job/artist-image-sync/main.go`
- `di.InitializeImageSyncJobApp()` で DI 構成
- `fanart IS NULL OR fanart_synced_at < now() - 7d` で対象選択（NULL 優先）
- Circuit breaker: 3 連続失敗で停止
- Exit 0（K8s リトライ防止）
- K8s CronJob マニフェスト（concert-discovery をテンプレートに）

## Risks / Trade-offs

**[fanart.tv にアーティスト画像がない]** → Artist.Fanart が空のまま。フロントエンドは既存の HSL カラーにフォールバック（現状維持）。特にインディーズ/ローカルアーティストでカバー率が低い可能性あり。

**[fanart.tv API ダウン]** → Retry + circuit breaker で制御。画像なしでもサービスの主機能（コンサート通知）には影響しない。

**[fanart.tv ToS 変更・サービス終了]** → JSONB カラムのデータは残る。別ソースへの移行時は `ArtistImageResolver` インターフェース実装を差し替えるだけ。

**[JSONB カラムサイズ]** → 1 アーティストあたり数 KB 程度（画像 URL のリスト）。数万アーティスト規模でも問題なし。
