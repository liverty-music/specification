## Context

現在、GCP Cloud Monitoring のアラート通知は Slack のみに送信されている。Slack Notification Channel は OAuth フローの制約により GCP Console で手動作成し、チャネル ID を Pulumi ESC に格納して参照している。

Google Chat が Workspace で利用可能になり、GCP Cloud Monitoring は 2023年10月から `google_chat` type の Notification Channel をサポートしている。Slack と異なり、Google Chat チャネルは API 経由で作成可能なため、Pulumi リソースとして完全に IaC 管理できる。

## Goals / Non-Goals

**Goals:**
- 既存の全 Alert Policy に Google Chat Notification Channel を追加し、Slack と並行で通知を受信
- Google Chat チャネルを Pulumi リソースとして作成・管理
- 環境ごとに異なる Chat スペースを使用（dev / prod）

**Non-Goals:**
- Slack チャネルの廃止（並行運用を維持）
- Alert Policy のフィルタ条件やレート制限の変更
- ArgoCD 通知の設定

## Decisions

### 1. Google Chat Notification Channel を Pulumi リソースとして作成

**選択**: `gcp.monitoring.NotificationChannel` を `monitoring.ts` 内で作成
**代替案**: Slack と同様に GCP Console で手動作成 → ID を ESC に格納
**理由**: Google Chat は OAuth 不要で `space_id` のみで API 作成可能。IaC 管理することでインフラの一貫性を保てる。

### 2. space_id を Pulumi ESC に格納

**選択**: ESC の `pulumiConfig.gcp.monitoring.googleChatSpaces.alertBackend` に space_id を格納
**代替案**: Pulumi config や定数ファイルにハードコード
**理由**: 環境ごとに異なる値で、既存の Slack チャネル ID と同じ管理パターンに揃える。

### 3. GcpConfig に googleChatSpaces フィールドを追加

**選択**: `monitoring` オブジェクト内に `slackNotificationChannels` と並列で `googleChatSpaces` を追加
**代替案**: 汎用の `notificationChannels` 配列に統合
**理由**: Slack と Google Chat は作成方法が異なる（Slack は参照のみ、Google Chat は Pulumi で作成）。型レベルで区別することで、各チャネル種別の扱いの違いを明示する。

### 4. MonitoringComponent の notificationChannels を統合配列で渡す

**選択**: `MonitoringComponent` 内部で Slack チャネル参照と Google Chat チャネルリソースの ID を1つの配列にまとめ、各 AlertPolicy に渡す
**理由**: Alert Policy 側は通知先の種類を区別しない。配列を結合するだけでよく、既存のアラート構造を変更せずに済む。

## Risks / Trade-offs

- **Google Chat スペースの Monitoring アプリ未インストール** → チャネル作成は成功するが通知が届かない。前提条件として手動インストールが必要（今回は済み）。
- **space_id の誤設定** → 通知が別のスペースに送られるか、チャネル作成が失敗する。ESC の値設定時に検証する。
- **Slack と Google Chat の二重通知** → 意図的な並行運用だが、通知疲れの可能性あり。運用を見て調整。
