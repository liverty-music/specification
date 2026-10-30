## Why

The backend commits a fact and then publishes its event in a second call: a failed publish is only logged, so the event is lost, and a retried call or a redelivered message publishes the same fact again under a new random id that no consumer can drop. Inside workflows the id comes from the step and a per-step counter, which is safe only when a step publishes the same list in the same order. Several "events" are not facts at all but requests to one receiver, and the payloads are hand-written structs that repeat the entities. `docs/event-delivery-design.md` (decided 2026-10-28) settles one model for all of them; this change carries it out.

## What Changes

- **An announcement is recorded with its fact.** Each entity operation that changes state announces the change in the same transaction, only when it changed something. The usecase no longer announces. A failure to record the announcement fails the operation and stores nothing. **BREAKING** for specs that let an announcement fail without failing the call.
- **One id per announcement, made when it is recorded** and kept on every delivery; consumers treat a repeated id as one. This replaces "An announcement from a workflow has one id" (step-derived ids) of the durable-workflows process spec.
- **No change, no announcement.** Operations that cannot tell today (Unfollow, SetHype, push subscription create and delete, PersistDrawOutcome, RecordRefund, UpdateDelivery, the TicketJourney upsert, Artist.Create, SeriesImage.Create) learn to. **BREAKING** for product analytics: a repeated hype level, an unfollow of an artist not followed, a repeated push subscription and a repeated payment notice are no longer reported; the refund announcement is no longer repeated until the email is sent; a series publish with no new Event announces nothing.
- **Requests become workflows, not events.** Asking one receiver to do work with no stored change behind it (send a notification, send a ticket sale reminder, resend a verification email, send a passkey recovery link, ingest found concerts) starts that receiver's workflow directly, named after its business key. Work that follows a stored change runs from that change's announcement. One exception: cover image processing runs in its own deployment (libvips), so SeriesImage.Create records the processing request, with the Series as its subject, in the outbox together with the SeriesImage. **BREAKING** (internal): subjects NOTIFICATION.requested, SALES_PHASE.reminder_due, USER.email_verification_resend_requested, USER.passkey_recovery_requested and CONCERT.discovered go.
- **Observations from outside are recorded as facts.** The passkey webhook starts the recording of the Passkey change, and the recorded Passkey is announced as added or removed; the passkey registered at sign-up is now emailed as added too. The login webhook records the User's last login time, and that change is announced.
- **Unused announcements go**: CONCERT.cancelled and ORGANIZER.concert_published have no receiver.
- **The payload is the changed entity**, or the entities of one type one operation changed together, as `entity/v1` messages in binary protobuf; the hand-written payload structs go. A fact that is not entity state becomes entity state or is read by id:
  - LotteryEntry gains the reason it lost (its sale and Order, and the referral code on the Order, come from `remodel-ticket-sales`).
  - An Artist names the Organizer that represents it, so the association announces the Artist.
  - A Passkey keeps the name the identity provider gave it, which the passkey email shows.
  - Every entity is compared with its proto, and a field left out for no personal-data reason is added.
- **Personal data and credentials**: an announcement may carry an email address and never the full name or phone number given for the ticket face, nor the display name from the identity provider, nor a push address or its keys.
- Code moves the entity-to-proto conversion to one package shared by the RPC handlers and the announcements, and removes the event publisher from the usecases.

## Capabilities

### New Capabilities

- `components/infrastructure/backend/process/event-delivery`: how every backend process records, delivers and receives announcements (recorded with the fact, one id, at least once, an undelivered announcement reported, no change no announcement, personal data and push credentials, requests as workflows).
- `components/entity/user/record-login`: records that the User signed in and announces it.
- `components/usecase/user/record-login`: records a sign-in reported by the identity provider.
- `components/adapter/fan/api/webhook/login-events`: the identity provider's sign-in notices become UserUseCase.RecordLogin.

### Modified Capabilities

Process:
- `components/infrastructure/backend/process/durable-workflows`: the step-derived event id requirement is removed (moved to event-delivery).

Entities (Purpose, edited in the main spec):
- `components/entity/lottery-entry` (Purpose): new attribute lost reason (not drawn, or card could not be charged).
- `components/entity/user` (Purpose): new attribute last login time.
- `components/entity/artist` (Purpose): new attribute organizer (the Organizer that represents it, at most one), drawn Organizer ||--o{ Artist.
- `components/entity/passkey` (Purpose): new attribute name (the label the identity provider gave the passkey, shown in the passkey email).

Entity operations that now announce their change, only when they change something:
- `components/entity/follow/follow`, `follow/unfollow`, `follow/set-hype`
- `components/entity/checkout/release`
- `components/entity/series/publish-events`
- `components/entity/series-image/create`: records the request to process the image for its Series together with it
- `components/entity/resale-listing/record-refund`
- `components/entity/resale-listing/list-sold-unrefunded`: no longer returns refunded listings whose sold email is not sent (the announcement is no longer repeated)
- `components/entity/push-subscription/create`, `push-subscription/delete`
- `components/entity/lottery-entry/persist-draw-outcome`
- `components/entity/organizer/compare-and-set-status`, `organizer/associate-artist`
- `components/entity/ticket-sale/upsert-discovered`
- `components/entity/user/create`
- `components/entity/concert/create`
- `components/entity/ticket/admit`
- `components/entity/order/issue`
- `components/entity/notification/update-delivery`
- `components/entity/ticket-journey/upsert`
- `components/entity/artist/create`
- `components/entity/passkey/create`, `passkey/delete`

Usecases that stop announcing, or whose trigger changes from an event to a started workflow or a direct call:
- `components/usecase/follow/follow`, `follow/unfollow`, `follow/set-hype`
- `components/usecase/checkout/release-expired`
- `components/usecase/series/publish`, `series/cancel`, `series/set-cover-image`
- `components/usecase/series-image/process`
- `components/usecase/resale-listing/refund-sold`
- `components/usecase/push-subscription/create`, `push-subscription/delete`
- `components/usecase/lottery-entry/run-draw`
- `components/usecase/organizer/create`, `organizer/reconcile-provisioning`, `organizer/associate-artist`
- `components/usecase/ticket-sale/discover-for-artist`, `ticket-sale/announce-discovered-sale`, `ticket-sale/scan-due-reminders`
- `components/usecase/ticket-sale-reminder/deliver-reminder`
- `components/usecase/user/create`, `user/resend-email-verification`, `user/reissue-email-verification`, `user/request-passkey-recovery`, `user/send-passkey-recovery-link`, `user/notify-passkey-change`
- `components/usecase/passkey/record-change`
- `components/usecase/concert-candidate/approve`, `concert/create-from-discovered`, `concert/search-new-concerts`, `concert/search-new-concerts-on-first-follow`
- `components/usecase/ticket/admit`
- `components/usecase/order/fulfill-payment`
- `components/usecase/notification/notify-new-concerts`, `notification/deliver`
- `components/usecase/ticket-journey/set-status`, `ticket-journey/mark-paid`
- `components/usecase/artist/search`, `artist/list-similar`, `artist/list-top`

Stories (requirements whose text still has the usecase announce):
- `stories/follow-an-artist`: a follow that cannot be announced is not stored and fails, instead of being left to the daily search.
- `stories/discover-new-concerts`: SearchNewConcerts starts CreateFromDiscovered instead of announcing the discovery.
- `stories/discover-artists`: an artist registered through ArtistUseCase.Create is announced by Artist.Create, so its first image check no longer waits for the daily run.

Also:
- `components/usecase/artist/create`: Create announces nothing itself, and Artist.Create announces the registered artist.

Adapters:
- `components/adapter/fan/api/webhook/passkey-events`: starts PasskeyUseCase.RecordChange for the notice instead of announcing it.
- `components/adapter/fan/api/rpc/user`: ResendEmailVerification starts the resend instead of announcing it.

Unchanged and why: consumers whose trigger is a fact that stays an announcement keep their trigger requirement (for example ConcertUseCase.SearchNewConcertsOnFirstFollow on a new follow, ArtistUseCase.ResolveCanonicalName on a created artist, TicketJourneyUseCase.MarkPaid on a paid Order). `users.name` is out of scope (decided 2026-10-28).

## Impact

- **backend**: one outbox table for every subject and its relay (the Watermill forwarder) in the workflow worker; entity operations write announcements on the repository transaction; the usecases lose the event publisher; new workflows for the six requests; the passkey and login webhooks call usecases; consumers read binary protobuf payloads; the entity-to-proto conversion moves out of the RPC mapper package; the step-derived event id code goes; migrations for the lottery entry's lost reason, `users.last_login_time`, `passkeys.name` and `series_images.series_id`.
- **specification**: `entity/v1` gains the `LotteryEntry` lost reason, `User` the last login time, `Artist` its organizer, `Passkey` its name and User, `SeriesImage` its Organizer, `PushSubscription` its device family, and the `Follow` and `ConcertList` messages, and any field the entity-to-proto audit finds missing (a proto release).
- **cloud-provisioning**: JetStream streams lose the removed subjects.
- **frontend**: none.
- **Order of changes**: `remodel-ticket-sales` → this change → `make-lottery-draw-durable` → `unify-order-issuance` → `resell-tickets-by-lottery`. This change's deltas of `persist-draw-outcome`, `run-draw`, `order/issue`, `checkout/release` and `release-expired` are written against the main specs as `remodel-ticket-sales` leaves them, and the three later changes are written on this one: entity operations announce, usecases do not, and work after a stored change starts from its announcement.
