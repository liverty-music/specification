## Why

dev 環境のバックエンドアプリケーションは severity 付きの構造化ログ (JSON) を Cloud Logging に出力しているが、ERROR レベルのログが発生しても検知する仕組みがない。サーバーエラーや障害が発生しても気付けず、ユーザー影響が拡大するリスクがある。Cloud Monitoring の Log-Based Alert と Error Reporting を活用し、追加インフラなし・月額 $0.30 程度のローコストで導入する。

## What Changes

- Cloud Monitoring に Google Chat と Email の Notification Channel を追加
- ワークロードごと (server, consumer, concert-discovery) に ERROR ログの Log-Based Alert Policy を作成
- GCP Error Reporting API を有効化し、ERROR ログの自動グルーピング・初回検出通知を利用可能にする
- Pulumi IaC に monitoring コンポーネントを追加し、上記リソースをコードで管理

## Capabilities

### New Capabilities

- `app-error-log-alerting`: ERROR レベルのアプリケーションログを検知し、Google Chat / Email に通知する仕組み

### Modified Capabilities

(なし — 既存のアプリケーションコードや spec に変更は不要)

## Impact

- **Infrastructure (Pulumi)**: `cloud-provisioning/src/gcp/components/` に monitoring コンポーネントを追加
- **GCP APIs**: `clouderrorreporting.googleapis.com` を新規有効化
- **GCP Resources**: NotificationChannel × 2, AlertPolicy × 3 を新規作成
- **Pulumi ESC**: Google Chat Space ID, 通知先メールアドレスを環境変数として追加
- **コスト**: Alert Policy 条件 3 × $0.10 = $0.30/月
- **アプリケーションコード**: 変更なし
