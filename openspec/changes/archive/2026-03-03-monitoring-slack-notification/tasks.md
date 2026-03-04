## 1. Update GcpConfig type

- [x] 1.1 Change `GcpConfig.monitoring` fields from `chatSpaceId` / `notificationEmail` to `slackChannelName: string` / `slackAuthToken: string` in `cloud-provisioning/src/gcp/components/project.ts`

## 2. Update MonitoringComponentArgs

- [x] 2.1 Replace `chatSpaceId` / `notificationEmail` with `slackChannelName` / `slackAuthToken` in `MonitoringComponentArgs` interface in `cloud-provisioning/src/gcp/components/monitoring.ts`

## 3. Replace Notification Channels

- [x] 3.1 Remove Google Chat `NotificationChannel` (`notification-google-chat`)
- [x] 3.2 Remove Email `NotificationChannel` (`notification-email`)
- [x] 3.3 Add Slack `NotificationChannel` with `type: "slack"`, `labels.channel_name`, and `sensitiveLabels.authToken`
- [x] 3.4 Update `notificationChannels` array to reference the single Slack channel
- [x] 3.5 Update `registerOutputs` to reflect the new channel structure

## 4. Update Gcp class integration

- [x] 4.1 Update `MonitoringComponent` instantiation in `cloud-provisioning/src/gcp/index.ts` to pass `slackChannelName` / `slackAuthToken` instead of `chatSpaceId` / `notificationEmail`

## 5. Verification

- [x] 5.1 Run lint and typecheck
- [x] 5.2 Run `pulumi preview` to confirm resource changes (2 channels removed, 1 added, 3 policies updated)
