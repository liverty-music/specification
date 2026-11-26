## Why

A fan who loses a lottery gets the loss email, but the Timetable and the concert sheet keep showing Applied (申込済) until the fan changes it by hand. The platform already records Applied and Paid from its own records, and it knows the loss too.

## What Changes

- When a fan's lottery entry is lost because it was not drawn or because the card could not be charged, the platform records Lost (落選) on the fan's ticket journey for the event.
- Nothing is recorded when the entry is lost because the concert was cancelled: the fan did not lose, and the cancellation has its own notice.
- Nothing is recorded while another lottery entry of the fan for the event is Entered or Won: its own result decides the journey.
- An open checkout or resale entry does not hold the Lost back. Neither runs this again when it ends, so waiting for it would leave Applied forever; a purchase writes Paid over Lost.
- The platform's Lost replaces only a journey at Tracking or Applied, or creates one. It never replaces Unpaid, Paid or a Lost the fan set.
- Official resale entries are unchanged: applying through resale does not mark a journey Applied, so losing one records nothing.
- No screen, RPC or proto changes.

## Capabilities

### New Capabilities

- `components/usecase/ticket-journey/mark-lost`: records Lost on a fan's journey after a lost lottery entry.

### Modified Capabilities

- `components/entity/ticket-journey` (Purpose): which journeys the platform's Lost may replace; the Purpose says the platform marks a lost entry Lost.
- `components/entity/ticket-journey/upsert-if-replaceable` (Purpose): the Purpose names the platform's Lost. Its requirement already refers to the entity's replacement rule and is unchanged.
- `stories/win-tickets-in-a-lottery` (Purpose): a lost entry marks the fan's journey Lost.

`entity/lottery-entry/list-by-user` and `entity/ticket-stock/get` are used as they are.

## Impact

- backend: the ticket journey replacement rule, a new usecase method and an event consumer on `LOTTERY_ENTRY.lost`.
- cloud-provisioning: a JetStream consumer and an autoscaling trigger for it.
- Entries lost before the release are not backfilled.
