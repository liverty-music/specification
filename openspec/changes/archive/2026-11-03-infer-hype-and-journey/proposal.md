## Why

Hype and the ticket journey are the fan's only explicit signals of interest in an artist and in an event, but few fans set them: in production most Follows are still at the default Nearby, and most fans have recorded no journey. The stored values cannot even say which hype levels a fan chose, because a chosen Nearby and the default Nearby are the same row. This change records who set each value and lets the app set the values a fan's own actions already reveal, so the signals become both more common and trustworthy.

## What Changes

- A Follow records who set its hype level: `default` (the level a new Follow starts at), `fan`, or `inference` (raised by the app). A hype level set by the fan is never changed by the app, and the app never lowers a hype level.
- A ticket journey records who set its status: `fan`, `platform` (a fact the platform itself recorded: an entered lottery, a paid Order), or `inference`.
- When the fan records Applied, Unpaid or Paid for a concert, or the platform records Applied or Paid for it, and the fan's hype level for its artist does not match the concert, the hype level is raised to the lowest level that matches it, unless the fan set it. On the event detail sheet the fan sees the raise in a snack and can undo it; the undo is the fan's own choice.
- A fan's lottery entry on the platform marks their journey for the event Applied, set by the platform, from the entry's announcement, so recording the journey never fails or delays the entry. A journey at Unpaid or Paid stays as it is.
- Adding a concert to the calendar from the event detail sheet starts tracking it (journey Tracking, set by inference) when the fan has no journey for it. When the fan returns to the app, a snack says so and offers undo; undo deletes the journey, and a later calendar add infers it again.
- Opening a new-concert push notification does not set any journey.
- A person without a home area is asked for one on the Dashboard and on My Artists, the two screens whose content depends on it: without a home, Home and Nearby match no concert, so hype levels and the Dashboard lanes have no meaning. The sheet cannot be closed by a signed-in fan or a guest in onboarding. Sign-up never asks for the home: a guest who signs up from an event page without one gets an account without a home and is asked on the next Dashboard or My Artists visit. A new fan picks the home before the post-signup celebration and dialog.
- A guest's hype level carries who set it (default or fan) into the account at sign-up, so a guest's chosen Nearby is kept as the fan's choice.
- The announcements of a changed hype level and a changed journey status carry who set the value, so product analytics can tell a fan's choice from the app's inference.
- The wording "hype covers a lane" and "hype radius includes" in the fan web specs is replaced by the entity term "hype matches a concert".
- New fan RPC `TicketJourneyService.InferTracking`; the entity messages `Follow` and `TicketJourney` gain who set the value.

## Capabilities

### New Capabilities
- `components/entity/follow/raise-hype`: raises a Follow's hype level to a given level, set by inference, only when the fan did not set it and the given level is higher.
- `components/entity/ticket-journey/upsert-if-replaceable`: stores a status set by the platform or by inference only over a journey it may replace.
- `components/usecase/ticket-journey/infer-tracking`: starts tracking an event the fan added to their calendar, when the fan has no journey for it.
- `components/usecase/ticket-journey/mark-applied`: records Applied, set by the platform, for each new lottery entry announced, and raises the hype level.

### Modified Capabilities
- `components/entity/follow` (Purpose): new attribute `hype set by`. Requirements: a new Follow starts at Nearby set by default; the rule for the hype level that matches a concert and for when the app may raise it.
- `components/entity/follow/follow`: the stored Follow is set by default.
- `components/entity/follow/set-hype`: SetHype records the level as set by the fan, also when the level stays the same, and its announcement carries who set it.
- `components/entity/follow/list-by-user`: each entry carries who set the hype level.
- `components/entity/ticket-journey` (Purpose): new attribute `status set by`; the platform marks Applied and Paid, the app starts Tracking. Requirements: which journeys the platform and the app may replace.
- `components/entity/lottery-entry/create`: a new entry is announced together with it.
- `components/entity/ticket-journey/upsert`: Upsert records who set the status, and its announcement carries it.
- `components/usecase/follow/set-hype`: the fan's level is recorded as set by the fan.
- `components/usecase/ticket-journey/set-status`: records the status as set by the fan and raises the hype level.
- `components/usecase/ticket-journey/mark-paid`: records Paid as set by the platform and raises the hype level.
  SetStatus, MarkPaid and MarkApplied (new) raise the level through Follow.RaiseHype after reading User.Get, Concert.ListByIDs and Follow.ListByUser; the three reads are unchanged apart from ListByUser above. InferTracking and MarkApplied rely on TicketJourney.UpsertIfReplaceable (new); MarkApplied also reads LotteryEntry.Get, which is unchanged. `LotteryEntryUseCase.Confirm` is not changed: the announcement is LotteryEntry.Create's.
- `components/adapter/fan/api/rpc/ticket-journey`: InferTracking acts for the signed-in fan and validates its request.
- `components/infrastructure/fan/web/global/event-detail-sheet`: the calendar add starts tracking with an undo snack on return; a hype raise after a journey change shows an undo snack.
- `components/infrastructure/fan/web/route/dashboard`: highlight wording uses "matches".
- `components/infrastructure/fan/web/global/live-highway`: "Hype Visual Indicators on Dashboard Cards" is replaced by "Dashboard cards show whether the hype level matches the concert", which uses "matches" and describes the matched and unmatched cards as the app renders them today (no logo, no color drift, a lighter gradient with grain for unmatched cards). (Purpose): the cards show the artist name, not a logo. The logo requirements (Event Card Logo Display, Logo and text visibility on unmatched cards, Center-aligned card content, Logo scales to fill card space) are removed: every card has shown the artist name as text since the frontend dropped logo images; "Artist name shown on every card" keeps the centering and full visibility, "Text fallback font size prominence" is renamed "Artist name larger than the location label" and no longer compares with a logo, and "Frontend Background Color Derivation" is removed (the card color comes from the artist name).
- `stories/set-hype-for-an-artist`: wording uses "matches"; a level the fan set is never changed by the app.
- `stories/track-ticket-journey` (Purpose): the usecase diagram adds TicketJourneyUseCase.InferTracking. Requirements: calendar inference, hype raise after a journey.
- `stories/win-tickets-in-a-lottery` (Purpose): the usecase diagram adds TicketJourneyUseCase.MarkApplied. Requirements: an entry marks the journey Applied.
- `stories/sign-up-or-sign-in`: a sign-up without a home creates the account without one and asks for the home later, on the Dashboard or My Artists.
- `components/infrastructure/fan/web/global/user-home-selector`: the Dashboard and My Artists ask a person without a home in the shared sheet, which a signed-in fan or a guest in onboarding cannot close; "Unified home area selector" lists My Artists among its uses.
- `stories/merge-guest-data-on-signup`: guest storage keeps who set the hype level, and the merge sends a level the guest set even when it is Nearby.

**Built on `publish-events-through-outbox`** (archived): the deltas of `entity/follow/set-hype`, `entity/ticket-journey/upsert`, `usecase/ticket-journey/set-status` and `usecase/ticket-journey/mark-paid` are written against the main specs as that change left them (entity operations announce their own changes; usecases send no signals). Its backend release must be in production before this change's backend work ships.

Not changed: `components/usecase/lottery-entry/run-draw`. Recording Lost for a lost lottery entry waits for the change `make-lottery-draw-durable`, which rewrites the draw; it is a follow-up.

## Impact

- **specification**: `proto/liverty_music/rpc/ticket_journey/v1/ticket_journey_service.proto` gains `InferTracking`; the doc comments of `User.home`, `UserService.Create` and `CreateRequest.home` revert to say the home is optional; the entity messages `Follow` and `TicketJourney` gain `hype_set_by` and `status_set_by` (the announcement payloads); `docs/analytics/event-catalog.md` gains the `set_by` property on `artist.hype.changed` and `ticket.journey.status.changed`.
- **backend**: migration adding `followed_artists.hype_set_by` and `ticket_journeys.status_set_by` with backfill; entity, repositories, `FollowUseCase.SetHype`, `TicketJourneyUseCase` (SetStatus, MarkPaid, new InferTracking and MarkApplied), the new subject `ORDER.lottery_entry_entered` and its consumer, the ticket journey RPC handler.
- **frontend**: event detail sheet (calendar inference, return snack, hype raise snack), follow store re-read after a journey change, guest storage and guest merge, and the home sheet on the Dashboard and My Artists for a person without a home.
- **cloud-provisioning**: the `ORDER.*` stream already captures the new subject; a durable consumer for MarkApplied.
- **Follow-ups**: lost lottery entry → journey Lost (after `make-lottery-draw-durable`, #1320); showing the effect of hype outside the help sheet (#1321); asking about the journey when the fan returns from the official site (#1322); the journey of a fan who resells their tickets (#1323).
