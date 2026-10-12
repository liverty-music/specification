# Spec Delta

## REMOVED Requirements

### Requirement: Registering a browser is always for the caller
**Reason**: PushNotificationService has no entity behind it. A browser's push subscription is the PushSubscription resource, so its Create, Get and Delete move to PushSubscriptionService under the RPC naming rule.
**Migration**: The behavior continues unchanged in `components/adapter/fan/api/rpc/push-subscription`; clients call `PushSubscriptionService.Create`.

### Requirement: Checking and removing a browser only for the caller
**Reason**: Get and Delete move to PushSubscriptionService, and the request no longer names the calling fan: the fan is taken from the sign-in (design D15), so the check that the named fan is the caller goes with the field.
**Migration**: The behavior continues in `components/adapter/fan/api/rpc/push-subscription`; clients call `PushSubscriptionService.Get(endpoint)` and `PushSubscriptionService.Delete(endpoint)` without a user id.

### Requirement: Direct new-concert push only outside production
**Reason**: NotifyNewConcerts is a test hook with no fan caller. It moves to the admin NotificationService, so PushNotificationService, which has no entity behind it, is removed.
**Migration**: The behavior continues in `components/adapter/admin/api/rpc/notification` as admin `NotificationService.NotifyNewConcerts`, which also requires the admin role.
