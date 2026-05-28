## Why

prod 環境の月次コストが想定を上回り、SKU レベルの調査で 3 つの即効性のある削減候補が見つかった: ① otel-collector が低価値な OTLP metric を素通しで Cloud Monitoring に流して billing account の free tier (150 MiB) を圧迫している、② prod overlay は semver pin 運用に変更済みなのに Argo CD の image-updater 等が常駐して Autopilot per-Pod 課金を発生させている、③ Cloud SQL prod インスタンスが launch 直後の SLA 要件を超える `REGIONAL` HA で動いており約 2 倍のコストを払っている。本 change はこの 3 点を 1 つの作業単位として並行で潰し、月 ¥3,250-3,600 (~11%) のコスト圧縮を行う。加えて、今回の調査が「BigQuery Billing Export が無いと SKU 別の日次分解ができず推測に頼らざるを得なかった」反省から、コスト調査基盤として ④ **BigQuery Billing Export 用の BQ dataset と IAM bindings を Pulumi 管理化**して恒久的な観測手段を整備する。

## What Changes

- otel-collector Deployment の `googlecloud` exporter pipeline に **filter processor** を追加し、`rpc.server.*` (5 metric) と `http.client.*` (2 metric) を OTLP レベルで drop(Cloud Monitoring 上では `workload.googleapis.com/rpc.server.*` と `workload.googleapis.com/http.client.*` として見えるが、filter processor は `googlecloud` exporter より前段で動くため OTLP 名で指定する)。残す metric は `concert.search.count` と `db.pool.{active,idle}_connections` の 3 種のみ。
- prod overlay (`k8s/namespaces/argocd/overlays/prod/`) で **Argo CD pod 数を最小化**: image-updater-controller を完全に disable、未使用なら notifications-controller / applicationset-controller も disable、argocd-server の replicas を 2 → 1 に。
- Cloud SQL prod の **`availabilityType` を REGIONAL → ZONAL** に変更し、HA レプリカを廃止。Pulumi (`postgres.ts` または環境設定) で切り替え、`pulumi up` で適用。短時間のダウンタイムを許容する。
- **BigQuery Billing Export** 用のリソース (BQ dataset `billing_export` + billing-export service account への IAM binding) を Pulumi で provision。実際の export 有効化操作 (Console 経由 or `gcloud billing` CLI) は手動で行うがそのための runbook を整備する。
- 上記 4 つの変更は互いに独立しており、リスクが大きい順に Cloud SQL を最後に置く。

## Capabilities

### New Capabilities
- `billing-export-infrastructure`: GCP Billing Export の受け皿となる BigQuery dataset と billing-export service account への IAM binding を Pulumi で provision する。Standard / Detailed / Pricing の各 export を同一 dataset に集約し、コスト分析 SQL の基盤として恒久運用する。

### Modified Capabilities
- `otel-collector-deployment`: metric pipeline の filter ポリシーを要件として追加。"OTLP で受け取った metric のうち、現在の運用で必要なものだけを Cloud Monitoring に export する" 振る舞いを規定する。
- `argocd-image-automation`: 「prod 環境では image-updater は無効」「prod は semver pin 経由でのみ image 更新」という運用ポリシーを明文化する。dev は現状通り auto-update を継続。
- `argocd-gateway-deployment`: prod overlay の Argo CD pod minimum 構成 (image-updater / notifications / applicationset の有効/無効と argocd-server のレプリカ数) を要件化する。
- `database`: prod の Cloud SQL availability に関する要件を「launch フェーズは ZONAL、本格運用フェーズで REGIONAL HA を選択する」段階的ポリシーに緩める。

## Impact

- 影響コード:
  - `cloud-provisioning/k8s/namespaces/otel-collector/base/configmap.yaml` (filter processor 追加)
  - `cloud-provisioning/k8s/namespaces/argocd/overlays/prod/` (image-updater 等の有効/無効、replicas 調整)
  - `cloud-provisioning/src/gcp/components/postgres.ts` または `Pulumi.prod.yaml` (availabilityType)
  - `cloud-provisioning/src/gcp/components/` 配下に **新規 `billing-export.ts` コンポーネント** (BQ dataset + IAM)
  - `cloud-provisioning/docs/runbooks/` に Billing Export 有効化手順を新規 runbook として追加
- 影響インフラ:
  - prod GKE クラスタの otel-collector Deployment が再起動 (数秒)
  - Argo CD pod 3 個が削除される(image-updater-controller 無効化、applicationset-controller 無効化、argocd-server を 2→1)。notifications-controller は active な Google Chat subscription を保持しているため維持し、sync-failed / health-degraded / sync-status-unknown のアラートは引き続き動く
  - Cloud SQL prod が REGIONAL → ZONAL 切り替え時に短時間 (数分以内) のダウンタイム
  - `liverty-music-prod` プロジェクトに新規 BQ dataset `billing_export` (asia-northeast1) と IAM binding が作成される
- 関連メトリクス: Cloud Monitoring の bytes_ingested、Autopilot Spot Pod mCPU/Memory、Cloud SQL Regional/Zonal Micro Instance の SKU 課金額
- リスク:
  - Cloud SQL ZONAL 化で zonal failover の自動冗長性を失う。トラフィック規模が拡大する前の段階で実施するため許容範囲。後で REGIONAL に戻す場合は同様の手順で可能。
  - Billing Export の Console 操作は手動で残るため、runbook の手順抜けによって export が有効化されない可能性がある。検証ステップ (24h 後の `bq ls` でテーブル生成確認) を runbook に含める。
