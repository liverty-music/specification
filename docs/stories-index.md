# User stories: index

Every user story of Liverty Music, grouped by who it is for. Use it to find a
story; read the story itself in its spec.

**The spec is the source.** Each story lives in
`openspec/specs/stories/<story>/spec.md`: its Purpose (condensed to one line
below), an `eventmodeling` diagram of the flow (31 of the 37 have one), and
its requirements and scenarios. The tests cite those scenarios with
`@spec stories/<story> "<scenario>"`; the last column lists the files that do.

Maps for people, built on these stories:

- [fan-story-map.md](fan-story-map.md) — a fan's first sessions (onboarding),
  step by step, with the guide moments.
- [organizer-console-story-map.md](organizer-console-story-map.md) — the
  organizer console, the source of its members' guide.

To see a fan story's screens in order, run the frontend's
`npm run e2e:flows && npx playwright show-report` (the tests tagged `@flow`).

Keep this index in step: a change that adds, renames or removes a story
updates its row. The Tests column was read from the `main` branches of
`frontend` and `backend` on 2026-11-21.

## Fans: getting started

| Story | What the person gets done | Tests |
|---|---|---|
| [complete-onboarding](../openspec/specs/stories/complete-onboarding/spec.md) | A new visitor goes from Welcome to a first timetable; onboarding ends once and for good. | [frontend: `onboarding-flow.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/functional/onboarding-flow.spec.ts)<br>[frontend: `complete-onboarding.guest.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/prod/complete-onboarding.guest.spec.ts) |
| [roam-app-as-guest](../openspec/specs/stories/roam-app-as-guest/spec.md) | A guest moves around the app freely; account-only features are hidden, not blocked. | [frontend: `roam-app-as-guest.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/functional/roam-app-as-guest.spec.ts)<br>[frontend: `settings-page.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/functional/settings-page.spec.ts) |
| [set-home-area](../openspec/specs/stories/set-home-area/spec.md) | A person sets the home area that decides the HOME lane, in onboarding and in Settings. | — none cites it yet |
| [sign-up-or-sign-in](../openspec/specs/stories/sign-up-or-sign-in/spec.md) | A person signs up or signs in with a passkey from a control they chose. | [frontend: `sign-up-or-sign-in.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/functional/sign-up-or-sign-in.spec.ts)<br>[frontend: `ticket-notify-sign-up.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/functional/ticket-notify-sign-up.spec.ts) |
| [merge-guest-data-on-signup](../openspec/specs/stories/merge-guest-data-on-signup/spec.md) | What a guest collected (follows, hype, home area) moves into the new account. | [frontend: `merge-guest-data-on-signup.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/functional/merge-guest-data-on-signup.spec.ts) |
| [verify-email-address](../openspec/specs/stories/verify-email-address/spec.md) | A new fan verifies their email address from the verification email. | — none cites it yet |
| [restore-session-on-cold-start](../openspec/specs/stories/restore-session-on-cold-start/spec.md) | A signed-in fan stays signed in when the app starts again. | [frontend: `restore-session-on-cold-start.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/functional/restore-session-on-cold-start.spec.ts) |

## Fans: artists and concerts

| Story | What the person gets done | Tests |
|---|---|---|
| [discover-artists](../openspec/specs/stories/discover-artists/spec.md) | A fan finds artists by name, popular charts or similar artists. | [backend: `discover_artists_story_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/database/rdb/discover_artists_story_test.go) |
| [follow-an-artist](../openspec/specs/stories/follow-an-artist/spec.md) | A fan follows an artist; a first concert search starts if none ran before. | — none cites it yet |
| [set-hype-for-an-artist](../openspec/specs/stories/set-hype-for-an-artist/spec.md) | A fan chooses how far they will travel for an artist (hype level). | [frontend: `infer-hype-and-journey.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/functional/infer-hype-and-journey.spec.ts) |
| [find-concerts-nearby](../openspec/specs/stories/find-concerts-nearby/spec.md) | A fan finds concerts near their area in a period and follows from one (a guest is offered sign-up). | [frontend: `find-concerts-nearby.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/functional/find-concerts-nearby.spec.ts) |
| [open-a-shared-event-link](../openspec/specs/stories/open-a-shared-event-link/spec.md) | A fan opens a shared event link and lands on the event's public page. | [frontend: `open-a-shared-event-link.authenticated.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/prod/open-a-shared-event-link.authenticated.spec.ts)<br>[frontend: `open-a-shared-event-link.guest.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/prod/open-a-shared-event-link.guest.spec.ts) |

## Fans: notifications

| Story | What the person gets done | Tests |
|---|---|---|
| [get-notified-of-new-concerts](../openspec/specs/stories/get-notified-of-new-concerts/spec.md) | A fan gets a push when matching concerts of a followed artist are added. | [backend: `new_concerts_story_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/database/rdb/new_concerts_story_test.go) |
| [hear-about-a-new-ticket-sale](../openspec/specs/stories/hear-about-a-new-ticket-sale/spec.md) | A fan tracking a tour is told once when a new ticket sale is published. | [backend: `ticket_sale_story_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/database/rdb/ticket_sale_story_test.go) |
| [get-reminded-of-ticket-sale-milestones](../openspec/specs/stories/get-reminded-of-ticket-sale-milestones/spec.md) | A fan tracking a tour is reminded before sales open and close. | [backend: `ticket_sale_story_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/database/rdb/ticket_sale_story_test.go)<br>[backend: `ticket_sale_reminder_uc_test.go`](https://github.com/liverty-music/backend/blob/main/internal/usecase/ticket_sale_reminder_uc_test.go) |
| [review-received-notifications](../openspec/specs/stories/review-received-notifications/spec.md) | A fan sees every notification in one place, with what is unread. | [frontend: `notification-center.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/functional/notification-center.spec.ts) |

## Fans: tickets

| Story | What the person gets done | Tests |
|---|---|---|
| [track-ticket-journey](../openspec/specs/stories/track-ticket-journey/spec.md) | A fan records where they stand in getting a ticket, and sees it everywhere. | [frontend: `infer-hype-and-journey.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/functional/infer-hype-and-journey.spec.ts)<br>[frontend: `ticket-notify-sign-up.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/functional/ticket-notify-sign-up.spec.ts) |
| [buy-tickets-first-come](../openspec/specs/stories/buy-tickets-first-come/spec.md) | A fan buys tickets first come, first served, and pays by card. | [frontend: `buy-tickets-first-come.authenticated.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/prod/buy-tickets-first-come.authenticated.spec.ts)<br>[backend: `first_come_story_integration_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/database/rdb/first_come_story_integration_test.go) |
| [win-tickets-in-a-lottery](../openspec/specs/stories/win-tickets-in-a-lottery/spec.md) | A fan enters a lottery; a winner is charged and gets tickets, a loser never is. | [frontend: `seat-types.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/functional/seat-types.spec.ts)<br>[backend: `first_come_story_integration_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/database/rdb/first_come_story_integration_test.go)<br>[backend: `lottery_story_integration_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/database/rdb/lottery_story_integration_test.go)<br>[backend: `order_issue_uc_test.go`](https://github.com/liverty-music/backend/blob/main/internal/usecase/order_issue_uc_test.go) |
| [attribute-a-purchase-to-a-referral-link](../openspec/specs/stories/attribute-a-purchase-to-a-referral-link/spec.md) | A purchase through a referral link is counted under its code for the Organizer. | [frontend: `attribute-a-purchase-to-a-referral-link.authenticated.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/prod/attribute-a-purchase-to-a-referral-link.authenticated.spec.ts)<br>[backend: `lottery_story_integration_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/database/rdb/lottery_story_integration_test.go)<br>[backend: `referral_story_integration_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/database/rdb/referral_story_integration_test.go) |
| [resell-a-ticket](../openspec/specs/stories/resell-a-ticket/spec.md) | A fan lists a ticket in official resale; a daily draw gives it to another fan. | [frontend: `resell-a-ticket.authenticated.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/prod/resell-a-ticket.authenticated.spec.ts)<br>[backend: `resale_draw_story_integration_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/database/rdb/resale_draw_story_integration_test.go)<br>[backend: `resale_story_integration_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/database/rdb/resale_story_integration_test.go) |
| [enter-a-venue-with-a-ticket](../openspec/specs/stories/enter-a-venue-with-a-ticket/spec.md) | A fan enters the venue with one QR code; venue staff scan it. | — none cites it yet |

## Fans: account

| Story | What the person gets done | Tests |
|---|---|---|
| [manage-passkeys](../openspec/specs/stories/manage-passkeys/spec.md) | A fan adds, sees and removes their passkeys. | — none cites it yet |
| [recover-sign-in-after-losing-passkeys](../openspec/specs/stories/recover-sign-in-after-losing-passkeys/spec.md) | A fan who lost every passkey gets back in with their verified email. | — none cites it yet |
| [delete-my-account](../openspec/specs/stories/delete-my-account/spec.md) | A fan deletes their account from Settings. | [frontend: `delete-my-account.guest.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/prod/delete-my-account.guest.spec.ts) |

## Organizers

| Story | What the person gets done | Tests |
|---|---|---|
| [bootstrap-owner-credentials-on-first-sign-in](../openspec/specs/stories/bootstrap-owner-credentials-on-first-sign-in/spec.md) | A new Organizer's owner sets up a passkey from one invitation email. | — none cites it yet |
| [sign-in-as-organizer](../openspec/specs/stories/sign-in-as-organizer/spec.md) | A member signs in to the organizer console, always into their own Organizer. | [backend: `organization_repository_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/zitadel/organization_repository_test.go) |
| [publish-an-organizer-concert](../openspec/specs/stories/publish-an-organizer-concert/spec.md) | An Organizer authors, publishes, corrects and cancels its concert. | [backend: `publish_concert_story_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/database/rdb/publish_concert_story_test.go) |
| [replace-a-concert-cover-image](../openspec/specs/stories/replace-a-concert-cover-image/spec.md) | An Organizer replaces its concert's cover image. | — none cites it yet |
| [run-an-event-from-the-organizer-console](../openspec/specs/stories/run-an-event-from-the-organizer-console/spec.md) | A member takes one event from draft to the door in the console. | [frontend: `organizer-story.spec.ts`](https://github.com/liverty-music/frontend/blob/main/e2e/functional/organizer-story.spec.ts)<br>[backend: `organizer_console_story_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/database/rdb/organizer_console_story_test.go) |
| [remove-a-cancelled-concert](../openspec/specs/stories/remove-a-cancelled-concert/spec.md) | A cancelled concert's fans are refunded and the event is removed (with an admin). | [backend: `cancelled_concert_story_integration_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/database/rdb/cancelled_concert_story_integration_test.go)<br>[backend: `concert_delete_test.go`](https://github.com/liverty-music/backend/blob/main/internal/infrastructure/database/rdb/concert_delete_test.go)<br>[backend: `order_refund_uc_test.go`](https://github.com/liverty-music/backend/blob/main/internal/usecase/order_refund_uc_test.go) |

## Admins

| Story | What the person gets done | Tests |
|---|---|---|
| [sign-in-to-admin-console](../openspec/specs/stories/sign-in-to-admin-console/spec.md) | An admin signs in to the admin console. | — none cites it yet |
| [review-concert-candidates](../openspec/specs/stories/review-concert-candidates/spec.md) | An admin reviews concerts held back from automatic publishing. | — none cites it yet |
| [delete-a-fan-account](../openspec/specs/stories/delete-a-fan-account/spec.md) | An admin deletes a fan's account at the fan's request. | — none cites it yet |
| [retire-an-organizer](../openspec/specs/stories/retire-an-organizer/spec.md) | An admin deactivates and deletes an Organizer that should no longer exist. | — none cites it yet |

## The platform

| Story | What the person gets done | Tests |
|---|---|---|
| [discover-new-concerts](../openspec/specs/stories/discover-new-concerts/spec.md) | Newly announced concerts reach the catalog with no one entering them. | — none cites it yet |
| [maintain-authenticated-session](../openspec/specs/stories/maintain-authenticated-session/spec.md) | The backend authenticates each request from its JWT. | — none cites it yet |
