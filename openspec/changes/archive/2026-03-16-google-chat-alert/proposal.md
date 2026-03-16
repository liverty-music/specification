## Why

Google Chat が Workspace で利用可能になったため、既存の Slack アラートに加えて Google Chat スペースにもアラート通知を送りたい。Slack と並行運用し、チームが Google Chat でもアラートを受け取れるようにする。

## What Changes

- GCP Cloud Monitoring の Notification Channel に Google Chat (`google_chat` type) を追加
- 既存の全 Alert Policy（backend ERROR log × 3 + Atlas migration failure）に Google Chat チャネルを紐づけ
- Google Chat チャネルは Pulumi でリソースとして作成・管理（Slack と異なり OAuth 不要で IaC 対応可能）
- 環境ごとに別の Chat スペースを使用（dev / prod）

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `app-error-log-alerting`: 通知先に Google Chat を追加。Slack と並行して Google Chat スペースにもアラート通知を送信する要件を追加。

## Impact

- **cloud-provisioning**: `monitoring.ts` に NotificationChannel リソース追加、Alert Policy の notificationChannels 配列に Google Chat チャネルを追加
- **cloud-provisioning**: `project.ts` の `GcpConfig` インターフェースに Google Chat 設定フィールド追加
- **cloud-provisioning**: `index.ts` の MonitoringComponent 呼び出しに新設定を渡す
- **Pulumi ESC**: 各環境に `space_id` を格納（dev: `AAQAU_szLxU`, prod: `AAQA2yo_JVw`）
- **前提条件**: 各 Chat スペースに Google Cloud Monitoring アプリがインストール済み（完了済み）
