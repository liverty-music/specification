## MODIFIED Requirements

### Requirement: One new_concerts notification requested per matched follower

For each matched follower, NotifyNewConcerts SHALL request one notification of type new_concerts carrying that follower's message; NotificationUseCase.Deliver records and delivers each requested notification after NotifyNewConcerts has made the request, for each follower on its own. A follower whose Notification cannot be recorded, or whose delivery fails, SHALL NOT affect the other followers or fail NotifyNewConcerts. The story stories/get-notified-of-new-concerts covers the whole flow from the added concerts to the fan's browsers. When a follower's request cannot be made, NotifyNewConcerts SHALL stop and fail so the trigger is retried; a repeated request for the same follower, artist and concerts is a new request, so the follower can be notified again; the later one replaces the earlier one on the follower's devices by the per-artist tag. Requesting once per follower and concerts waits for a follow-up change (design, "One kind of CloudEvent id"). When the followers cannot be read, NotifyNewConcerts SHALL fail and request nothing. When the call is cancelled, no further follower's notification SHALL be requested.

#### Scenario: Every matched follower is requested

- **WHEN** three followers are matched
- **THEN** one new_concerts notification is requested for each of the three, carrying that follower's message

#### Scenario: Request fails for one follower

- **WHEN** the notification for the second of three matched followers cannot be requested
- **THEN** the third follower's notification is not requested and NotifyNewConcerts fails so the trigger is retried

#### Scenario: Same concerts notified twice

- **WHEN** NotifyNewConcerts runs twice within 2 minutes for the same artist and concerts and matches the same follower
- **THEN** two requests are made for the follower, and the second replaces the first on the follower's devices
