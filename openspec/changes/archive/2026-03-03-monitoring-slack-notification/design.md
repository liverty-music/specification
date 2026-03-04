## Context

monitoring-app-error-log change で MonitoringComponent を実装済み。Google Chat + Email の NotificationChannel と 3 つの AlertPolicy が Pulumi IaC で管理されている。しかし、現在の Google Workspace 環境ではメールと Chat が利用できないため、通知先を Slack に切り替える必要がある。

現在の `MonitoringComponentArgs` は `chatSpaceId: string` と `notificationEmail: string` を受け取る構造。`GcpConfig.monitoring` も同様のフィールドを持つ。

Slack App 自体は Pulumi/Terraform で管理できない (Provider が App 作成をサポートしていない) ため、手動で作成して Token を取得する必要がある。

## Goals / Non-Goals

**Goals:**

- 通知先を Google Chat + Email から Slack に変更する
- Slack Bot OAuth Token を secret として安全に管理する
- 既存の AlertPolicy ロジック (フィルタ、labelExtractors、alertStrategy) は変更しない
- NotificationChannel を 2 → 1 に削減する (Slack のみ)

**Non-Goals:**

- Slack App の IaC 管理 (Provider が未対応のため手動)
- 複数チャンネルへの通知振り分け
- Slack のインタラクティブ機能 (ボタン、スレッド返信等)
- prod / staging 環境への展開

## Decisions

### 1. Slack 通知チャネル 1 本に統合

**選択:** Google Chat + Email の 2 チャネルを Slack 1 チャネルに統合

**代替案:** Slack + Email の 2 チャネルを維持する

**理由:** メールが利用できないため Email チャネルはそもそも使えない。Slack 側のチャンネル通知設定で十分なフォールバックが確保できる。将来的にバックアップチャネルが必要になれば追加可能。

### 2. `sensitiveLabels.authToken` で Token を管理

**選択:** Pulumi の `sensitiveLabels` ブロックを使用し、`authToken` を GCP API 上で秘匿化する

**代替案:** `labels.auth_token` に直接 Token を格納する

**理由:** `labels` に格納すると API レスポンスで Token が平文返却される。`sensitiveLabels` を使えば GCP 側で秘匿化され、Pulumi state でも `pulumi.secret()` で暗号化される。公式ドキュメントでもこの方法が推奨されている。

### 3. `GcpConfig.monitoring` の型を Slack 向けに変更

**選択:** `chatSpaceId` / `notificationEmail` を `slackChannelName` / `slackAuthToken` に置き換える

**理由:** Chat/Email のフィールドが残っていると混乱の原因になる。monitoring-app-error-log の PR はマージ済みだが、ESC にまだ値を設定していないため、破壊的変更のリスクはない。

## Risks / Trade-offs

**[Slack App の手動管理]** → App の作成・権限設定は 1 回限りの作業。Token は長期間有効だが、Workspace の設定変更で失効する可能性がある。失効時は Slack App の OAuth & Permissions ページから再生成して ESC を更新する。

**[sensitiveLabels は API で読み取り不可]** → Pulumi が upstream の変更を検出できない。GCP Console から手動で変更された場合、Pulumi の state と乖離する。IaC 以外からの変更を禁止する運用ルールで対応する。

**[Slack の rate limit]** → Slack API には rate limit がある。しかし Cloud Monitoring 側の `notificationRateLimit.period = 43200s` で通知頻度を抑制しているため、Slack 側の rate limit に達する可能性は極めて低い。
