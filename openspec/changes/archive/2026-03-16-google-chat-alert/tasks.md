## 1. Pulumi ESC Configuration

- [x] 1.1 Add `pulumiConfig.gcp.monitoring.googleChatSpaces.alertBackend` to `liverty-music/dev` ESC environment with space_id `AAQAU_szLxU`
- [x] 1.2 Add `pulumiConfig.gcp.monitoring.googleChatSpaces.alertBackend` to `liverty-music/prod` ESC environment with space_id `AAQA2yo_JVw`

## 2. GcpConfig Interface Update

- [x] 2.1 Add `googleChatSpaces` field to the `monitoring` object in `GcpConfig` interface (`project.ts`)

## 3. MonitoringComponent Update

- [x] 3.1 Add `googleChatSpaceIds` parameter to `MonitoringComponentArgs` interface (`monitoring.ts`)
- [x] 3.2 Create `gcp.monitoring.NotificationChannel` resource with type `google_chat` and `space_id` label (`monitoring.ts`)
- [x] 3.3 Merge Slack channel references and Google Chat channel IDs into a single `notificationChannels` array for Alert Policies (`monitoring.ts`)

## 4. Integration

- [x] 4.1 Pass `googleChatSpaces` config from `index.ts` to `MonitoringComponent`

## 5. Verification

- [x] 5.1 Run `make lint-ts` to verify TypeScript compiles without errors
- [x] 5.2 Run `pulumi preview` on dev stack to verify resource changes
