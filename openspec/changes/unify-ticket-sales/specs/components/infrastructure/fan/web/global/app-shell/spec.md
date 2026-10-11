# Spec Delta

## MODIFIED Requirements

### Requirement: Push subscription recovered on launch

When the app opens, and again whenever the Service Worker reports that the browser's push subscription changed, the app SHALL check, for a signed-in fan whose account is loaded and who has granted notification permission, whether the server still has the browser's push subscription (PushSubscriptionService.Get). When the server answers NotFound, the app SHALL register the subscription again (PushSubscriptionService.Create) without asking the fan. When permission is not granted, the app SHALL do nothing and SHALL NOT show a permission prompt.

#### Scenario: Server lost the subscription

- **WHEN** a signed-in fan with notifications allowed opens the app and the server no longer has the browser's subscription
- **THEN** the subscription is registered again and the fan keeps receiving pushes without re-enabling them

#### Scenario: Permission not granted

- **WHEN** the fan has not granted notification permission
- **THEN** nothing is registered and no prompt is shown
