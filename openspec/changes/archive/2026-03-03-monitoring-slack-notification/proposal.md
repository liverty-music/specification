## Why

monitoring-app-error-log で導入した Cloud Monitoring の通知チャネルは Google Chat + Email を前提としていたが、現在の Google Workspace 環境ではメールと Chat が利用できないことが判明した。代わりに Slack に通知を送る必要がある。

## What Changes

- Google Chat Notification Channel を Slack Notification Channel に置き換える
- Email Notification Channel を削除する (メールも利用不可のため)
- `MonitoringComponentArgs` の `chatSpaceId` / `notificationEmail` を `slackChannelName` / `slackAuthToken` に変更
- `GcpConfig.monitoring` の型定義を Slack 向けに変更
- Pulumi ESC に Slack Bot OAuth Token を secret として格納する (viewable ではなく secret)

## Capabilities

### New Capabilities

(なし — 既存の `app-error-log-alerting` の通知チャネルを変更するのみ)

### Modified Capabilities

- `app-error-log-alerting`: 通知先を Google Chat + Email から Slack に変更

## Impact

- **Infrastructure (Pulumi)**: `cloud-provisioning/src/gcp/components/monitoring.ts` の NotificationChannel を Slack 型に変更
- **Pulumi ESC**: `chatSpaceId` / `notificationEmail` を `slackChannelName` / `slackAuthToken` に変更。`slackAuthToken` は secret として管理
- **GCP Resources**: NotificationChannel が 2 (Chat + Email) から 1 (Slack) に変更。AlertPolicy × 3 は変更なし
- **手動作業**: Slack App の作成、OAuth Token 取得、チャンネルへの Monitoring App 招待が必要 (1 回のみ)
- **コスト**: 変更なし ($0.30/月)
- **アプリケーションコード**: 変更なし
