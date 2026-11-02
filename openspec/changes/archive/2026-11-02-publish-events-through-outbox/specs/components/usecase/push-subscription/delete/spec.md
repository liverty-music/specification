## REMOVED Requirements

### Requirement: Delete removes the browser and announces it
**Reason**: PushSubscription.Delete announces a removed PushSubscription together with the removal (components/entity/push-subscription/delete), so the usecase no longer announces, and removing a browser that is not registered is no longer announced.
**Migration**: Replaced by "Delete removes the browser". Product analytics receives the "unsubscribed" signal, with the device family derived from the push address, from PushSubscription.Delete's announcement, for removals only. A failure to announce now fails Delete and leaves the PushSubscription in place.

## ADDED Requirements

### Requirement: Delete removes the browser

Delete SHALL remove the fan's PushSubscription for the push address through PushSubscription.Delete and succeed, also when nothing was registered. When PushSubscription.Delete fails, Delete SHALL fail with that error.

#### Scenario: Fan disables push on one browser

- **WHEN** a fan with two registered browsers removes one
- **THEN** that PushSubscription is removed and the other remains

#### Scenario: Browser not registered

- **WHEN** the fan has no PushSubscription with that push address
- **THEN** Delete succeeds and nothing is removed

#### Scenario: Removal fails

- **WHEN** PushSubscription.Delete fails with Unavailable
- **THEN** Delete fails with Unavailable and the PushSubscription remains
