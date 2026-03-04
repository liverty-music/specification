## 1. GCP API 有効化

- [x] 1.1 `GoogleApis` 型に `clouderrorreporting.googleapis.com` を追加 (`cloud-provisioning/src/gcp/services/api.ts`)
- [x] 1.2 `project.ts` の有効化 API リストに `clouderrorreporting.googleapis.com` を追加

## 2. Pulumi ESC 設定値の追加

- [ ] 2.1 Google Chat Space ID を Pulumi ESC に追加 (事前に Chat Space で Google Cloud Monitoring アプリをインストールし Space ID を取得)
- [ ] 2.2 通知先メールアドレスを Pulumi ESC に追加
- [x] 2.3 `GcpConfig` 型に `monitoring` フィールド (`chatSpaceId`, `notificationEmail`) を追加

## 3. MonitoringComponent の実装

- [x] 3.1 `cloud-provisioning/src/gcp/components/monitoring.ts` を新規作成
- [x] 3.2 Google Chat 用の `gcp.monitoring.NotificationChannel` を実装 (`type = "google_chat"`)
- [x] 3.3 Email 用の `gcp.monitoring.NotificationChannel` を実装 (`type = "email"`)
- [x] 3.4 server ワークロード用の `gcp.monitoring.AlertPolicy` を実装 (Log-Based Alert, `conditionMatchedLog` with `labelExtractors`)
- [x] 3.5 consumer ワークロード用の `gcp.monitoring.AlertPolicy` を実装
- [x] 3.6 concert-discovery ワークロード用の `gcp.monitoring.AlertPolicy` を実装
- [x] 3.7 Alert Policy の `alertStrategy` に `notificationRateLimit.period = "43200s"` と `autoClose = "3600s"` を設定

## 4. 統合

- [x] 4.1 `Gcp` クラス (`cloud-provisioning/src/gcp/index.ts`) に `MonitoringComponent` のインスタンス化を追加
- [x] 4.2 `pulumi preview` で差分を確認し、意図通りのリソースが作成されることを検証
