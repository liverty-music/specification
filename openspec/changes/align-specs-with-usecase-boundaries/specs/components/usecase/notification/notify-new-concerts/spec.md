# Spec Delta

## ADDED Requirements

### Requirement: One new_concerts notification requested per matched follower

For each matched follower, NotifyNewConcerts SHALL request one notification of type new_concerts carrying that follower's message; NotificationUseCase.Deliver records and delivers each requested notification after NotifyNewConcerts has made the request, for each follower on its own. A follower whose Notification cannot be recorded, or whose delivery fails, SHALL NOT affect the other followers or fail NotifyNewConcerts. The story stories/get-notified-of-new-concerts covers the whole flow from the added concerts to the fan's browsers. When a follower's request cannot be made, NotifyNewConcerts SHALL stop and fail so the trigger is retried; a request repeated within 2 minutes for the same follower, artist and concerts SHALL reach the follower only once, and a later repeat is replaced on the follower's devices by the per-artist tag. When the followers cannot be read, NotifyNewConcerts SHALL fail and request nothing. When the call is cancelled, no further follower's notification SHALL be requested.

#### Scenario: Every matched follower is requested

- **WHEN** three followers are matched
- **THEN** one new_concerts notification is requested for each of the three, carrying that follower's message

#### Scenario: Request fails for one follower

- **WHEN** the notification for the second of three matched followers cannot be requested
- **THEN** the third follower's notification is not requested and NotifyNewConcerts fails so the trigger is retried

#### Scenario: Same concerts notified twice

- **WHEN** NotifyNewConcerts runs twice within 2 minutes for the same artist and concerts and matches the same follower
- **THEN** the follower's two requests are the same request and the follower is notified once

## REMOVED Requirements

### Requirement: One new_concerts notification per matched follower

**Reason**: NotifyNewConcerts no longer records or sends the notifications itself. It requests one per matched follower, and NotificationUseCase.Deliver records and sends each on its own, so a recording failure for one follower no longer stops or fails the batch.

**Migration**: Replaced by "One new_concerts notification requested per matched follower"; recording and sending are stated in components/usecase/notification/deliver.
