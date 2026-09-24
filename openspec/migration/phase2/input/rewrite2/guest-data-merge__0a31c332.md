<!-- spec: guest-data-merge | target: stories/merge-guest-data-on-signup | flags: CLASSNAME | new_name: Guest Data Cleanup -->
<!-- implementation names to remove: UserStore -->

### Requirement: Guest Data Cleanup

The system SHALL remove guest data from LocalStorage after a successful
migration or when the user starts a fresh tutorial. Each store SHALL clear its
own guest data; sign-out clearing SHALL be triggered by the `SignedOut` event
and SHALL be idempotent and order-independent across stores.

#### Scenario: Cleanup after successful migration

- **WHEN** a store's migration completes successfully
- **THEN** that store SHALL remove its own guest keys from LocalStorage
  (`UserStore`: `guest.home` and the anonymous-period `language` key;
  follow store: `guest.followedArtists`)

#### Scenario: Cleanup on sign-out

- **WHEN** the user signs out
- **THEN** a `SignedOut` event SHALL be published
- **AND** each store SHALL clear its own state idempotently, independent of order

#### Scenario: Cleanup on fresh tutorial start

- **WHEN** a user taps [Get Started] on the LP to begin the tutorial
- **AND** stale guest keys exist in LocalStorage
- **THEN** the system SHALL clear those keys before starting Step 1
