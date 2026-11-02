# components/entity/push-subscription/delete-gone Specification

## Purpose
Removes the PushSubscription of one fan's browser that the push service reported gone, so no further message is sent to it. It is not the fan's own removal, so product analytics does not count it as an unsubscription.

## Requirements

### Requirement: DeleteGone removes only that pair and announces nothing

DeleteGone SHALL remove the PushSubscription with the given endpoint when it belongs to the given fan, and nothing else: the fan's other browsers and other fans' subscriptions stay. When no PushSubscription of that fan has that endpoint, DeleteGone SHALL succeed and change nothing. DeleteGone SHALL announce nothing.

#### Scenario: Gone browser removed

- **WHEN** DeleteGone runs for one of the fan's PushSubscriptions
- **THEN** that PushSubscription is removed, the fan's other browsers keep theirs, and nothing is announced

#### Scenario: Already removed

- **WHEN** no PushSubscription of the fan has the endpoint
- **THEN** DeleteGone succeeds and changes nothing
