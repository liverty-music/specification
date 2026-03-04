## Context

dev 環境のバックエンドは GKE Autopilot 上で 3 ワークロード (server, consumer, concert-discovery) が稼働し、`pannpers/go-logging` (slog wrapper) で JSON 構造化ログを stdout に出力している。GKE エージェントが自動で Cloud Logging に取り込み、`severity` フィールドも正しく認識されている。

Cloud Logging / Monitoring / Trace の API は有効化済みで、SA には `logging.logWriter` と `monitoring.metricWriter` ロールが付与されている。しかし、アラートポリシーと通知チャネルが存在しないため、ERROR ログが発生しても検知できない状態。

Pulumi IaC (`cloud-provisioning/`) で全インフラを管理しており、コンポーネントパターン (`components/`) で構造化されている。

## Goals / Non-Goals

**Goals:**

- ERROR レベルのログ発生時に Google Chat と Email で通知を受け取れるようにする
- ワークロードごとに独立したアラートポリシーを持ち、どのワークロードでエラーが発生したか即座に判別できるようにする
- 通知のノイズを抑制する (12 時間に 1 回まで)
- Error Reporting を有効化し、エラーの自動グルーピングと初回検出通知を利用可能にする
- 全リソースを Pulumi IaC で管理する

**Non-Goals:**

- WARN レベルのアラート (将来的に追加可能)
- カウントベースの閾値アラート (Log-Based Metric は今回のスコープ外)
- ダッシュボード作成
- prod / staging 環境への展開 (dev で検証後に別途対応)
- アプリケーションコードの変更

## Decisions

### 1. Cloud Monitoring Log-Based Alert を採用

**選択:** GCP ネイティブの Log-Based Alert Policy を使用する

**代替案:**
- Grafana + Loki: 高機能だが、dev 環境のみのためにデプロイ・運用するのはオーバーキル
- SigNoz: OTel ネイティブで魅力的だが、ClickHouse の運用負荷が追加される
- GCP Log-Based Metric + Metric Alert: カウントベースの閾値制御が可能だが、現時点では不要な複雑さ

**理由:** 既に Cloud Logging にログが流れており、追加インフラゼロ・月額 $0.30 で実現できる。Log-Based Alert は「ログエントリ一致で発火」するシンプルな仕組みで、dev 環境の初期監視に適切。

### 2. ワークロードごとに Alert Policy を分離

**選択:** server, consumer, concert-discovery それぞれに独立した Alert Policy を作成 (計 3 つ)

**代替案:** 1 つの Alert Policy で `resource.labels.namespace_name="backend"` のみでフィルタする

**理由:** ワークロードごとに分けることで、通知メッセージからどのコンポーネントでエラーが発生したか即座に判別可能。Alert Policy 名にワークロード名を含めることで、Google Chat の通知にもワークロード名が表示される。コスト差は $0.20/月で無視できる。

### 3. Notification Channel は Google Chat (primary) + Email (backup)

**選択:** 2 つの Notification Channel を作成し、全 Alert Policy で両方を指定する

**理由:** Google Chat はリアルタイム通知に適しているが、Chat Space の障害やアプリ未インストール時のフォールバックとして Email を確保する。

### 4. Pulumi コンポーネントとして `monitoring.ts` を新設

**選択:** `cloud-provisioning/src/gcp/components/monitoring.ts` に `MonitoringComponent` を新設する

**代替案:** 既存の `project.ts` に追加する

**理由:** 関心の分離。他のコンポーネント (kubernetes.ts, postgres.ts 等) と同じパターンに従う。将来的にダッシュボードや追加のアラートを追加する際にも拡張しやすい。

### 5. labelExtractors で error_code と rpc_method を抽出

**選択:** Alert Policy の `conditionMatchedLog` で `labelExtractors` を使い、`jsonPayload.error.code` と `jsonPayload.rpc_method` を抽出する

**理由:** 通知メッセージにエラーコード (`internal`, `unavailable` 等) と RPC メソッド名が含まれるようになり、通知を見ただけでエラーの種類と発生箇所が分かる。Cloud Logging へのリンクは通知に自動的に含まれるため、詳細確認もワンクリック。

### 6. Error Reporting API の有効化

**選択:** `clouderrorreporting.googleapis.com` を `GoogleApis` 型と `project.ts` の有効 API リストに追加する

**理由:** ERROR ログを自動でグルーピングし、新しいエラーパターンの初回検出を通知してくれる。追加コストなし。既存の JSON ログフォーマット (severity + message + optional stack trace) と互換性がある。

## Risks / Trade-offs

**[Log-Based Alert はカウントベース閾値が使えない]** → dev 環境では `notificationRateLimit.period = 43200s` (12 時間) で抑制しているため、実質的に問題にならない。将来的に閾値制御が必要になった場合は Log-Based Metric + Metric Alert に切り替える。

**[Google Chat Notification Channel には事前に Monitoring アプリのインストールが必要]** → 手動作業が 1 ステップ発生する。Chat Space で Google Cloud Monitoring アプリをインストールし、Space ID を取得して Pulumi ESC に設定する必要がある。

**[Error Reporting は Go の構造化ログと完全互換ではない可能性]** → Error Reporting は `reportLocation` や `serviceContext` の標準フィールドを期待する場合がある。go-logging のフォーマットで自動検出されない場合は、別途対応が必要になるが、severity=ERROR の JSON ログは最低限検出される。

**[autoClose = 3600s の場合、断続的なエラーで Incident が頻繁に Open/Close を繰り返す可能性]** → notificationRateLimit が 12 時間なので、通知自体は抑制される。Incident の Open/Close はログとして残るが実害はない。
