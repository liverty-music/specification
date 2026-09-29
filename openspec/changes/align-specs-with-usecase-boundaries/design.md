## Context

The specs are rewritten to match backend main 120bd90 (see proposal.md, Why). The implementation shipped in liverty-music/backend#517, #518, #519 and #520; #516 only corrected Go comments that the specs already stated correctly. The only code still owed is:

- Deleting OrganizerUseCase.GetByZitadelOrgID.
- Adding the tests that carry `@spec` annotations.

## Goals / Non-Goals

**Goals:**
- Every spec names the usecase method that ships and describes its shipped failure handling.
- Every added or modified scenario is verified by an annotated test, or is listed below as `@spec-manual`.

**Non-Goals:**
- Changing any shipped behavior, apart from deleting the dead OrganizerUseCase.GetByZitadelOrgID.
- The contradiction between `stories/complete-onboarding` (the app calls SearchNewConcerts during onboarding) and `stories/follow-an-artist` (the app never starts a search after a follow). A separate issue tracks it.
- Making the resend limit hold across server instances (see Risks).

## Decisions

- **Internal events are triggers of the usecase they run, not components.** This follows the schema. The follow announcement (ARTIST.followed) and the per-recipient notification request (NOTIFICATION.requested) are therefore written as the trigger requirements of ConcertUseCase.SearchNewConcertsOnFirstFollow and NotificationUseCase.Deliver. No adapter spec is added for the event consumers.
  - Retries come from the consumer router: up to 3 retries with exponential backoff from 500 ms, then the message goes to a poison queue.
  - The specs say only "processed again", as `usecase/media/process-media` already does.
- **Duplicate requests are deduplicated by the broker.** The producers derive each notification request's id deterministically:
  - For new concerts: type + recipient + artist + concert ids.
  - For sales-phase announcements: type + recipient + phase.
  - The NOTIFICATION stream then drops a request whose id it has seen within its 2-minute Duplicates window.
  - The specs state the observable effect: a repeat within 2 minutes reaches the fan once, and a later repeat is replaced on the device by the message tag. The broker and the id scheme stay here.
- **DeliverReminder keeps its synchronous path.** It records and sends through the same delivery logic as Deliver, but without calling NotificationUseCase, so its spec is unchanged.
- **Caller resolution: the boundary passes, the usecase decides.** The boundary still reads the caller's tenant or identity from the sign-in. The active-Organizer rule and the "named User is the caller" rule now belong to OrganizerUseCase.ResolveCaller and UserUseCase.ResolveCaller. The adapter specs keep their caller-visible scenarios and refer to those usecases for the rule, as the schema assigns role and ownership preconditions to the usecase.
- **The main spec for GetByZitadelOrgID is removed by delta, then its directory is deleted.** The spec is removed through a REMOVED delta of its only requirement, as the removal decision asks. If archive leaves the main spec with a Purpose and no requirements, the archiving PR deletes the directory directly. The schema treats that as a main-spec edit, not a change.
- **The spec move is a separate direct commit.** `notification/notify` moved to `notification/deliver` in a commit before this change, with its mapping table, so the deltas here target the new path.

## Risks / Trade-offs

- [The resend limit is not cluster-wide] The spec states the intended rule: 3 per 10 minutes per User. The shipped limit is kept in each server instance's memory. It is not shared across replicas and it resets when an instance restarts, so the effective limit is 3 per replica per 10 minutes. → Known limitation, tracked by a follow-up issue. The fix is a shared store for the counter.
- [A failed follow announcement skips the first search] The artist waits for the daily search at 18:00 JST. Before #520 the search ran in the background regardless. → Accepted; the story states it.
- [A retried first-follow search usually does nothing] SearchNewConcerts records the SearchLog before searching, so a retry after a failed search finds a SearchLog and does nothing. The artist is picked up by the daily search. → Accepted; the usecase spec states it.

## Migration Plan

1. Merge this planning PR.
2. Implement tasks.md in one backend PR: delete the method, add the tests and annotations.
3. After it merges, run `/opsx:verify` and `/opsx:archive`. In the archiving PR, delete `openspec/specs/components/usecase/organizer/get-by-zitadel-org-id/` if archive left it without requirements.

Rollback: revert the backend PR. The spec change describes behavior that already ships.

## Manual verification of story scenarios

The stories have no automated E2E test for these scenarios. Each is verified on the dev environment as follows:

@spec-manual stories/follow-an-artist "Never-searched artist with announced concerts" -- dev is decommissioned and the local compose stack has no NATS, so verify on prod after the first backend release that contains backend#520: sign in as a test fan and follow, from Discovery, an artist that has no search log row. Confirm that the event-consumer logs "processing ARTIST.followed event for first-follow search" for that artist, that a search log row appears, and that once it completes the artist's newly found concerts are in the catalog and on the fan's Dashboard.
@spec-manual stories/follow-an-artist "Artist searched before" -- On prod after that release, follow an artist whose search log row already exists. Confirm that the event-consumer logs no first-follow search for it, that the row's updated time is unchanged, and that the Dashboard shows the artist's existing concerts.
@spec-manual stories/follow-an-artist "Several fans follow a new artist at once" -- On prod after that release, follow the same never-searched artist from two test fans within 5 seconds. After both searches finish, confirm that each discovered concert exists once in the catalog (no duplicate event for the same venue, date and start time).
@spec-manual stories/follow-an-artist "Follow not announced" -- Covered by the annotated unit tests for `components/usecase/follow/follow` "Announcement fails" and `components/usecase/concert/search-new-concerts-on-first-follow` "Follow announced". In code review of the backend PR, also confirm that the first-follow search is wired only to ARTIST.followed in the consumer's behavior table, and that the daily concert search covers every followed artist.
@spec-manual stories/get-notified-of-new-concerts "Away follower with one browser" -- The NotifyNewConcerts RPC is non-production only and dev is decommissioned, so verify on prod after the first backend release that contains backend#520, using the next organic CONCERT.created fan-out: for a test fan who follows the artist at Away and has allowed push in one browser, confirm that the browser shows one push titled with the artist's name, counting the new concerts and linking to the earliest one, and that the fan's new_concerts notification row is Delivered.
@spec-manual stories/get-notified-of-new-concerts "Matched follower without a browser" -- In the same prod fan-out, query the notifications table for a matched follower with no registered browser and confirm that their new_concerts row is Failed with the reason "no active push subscription".
@spec-manual stories/get-notified-of-new-concerts "Watch follower" -- In the same prod fan-out, confirm that a follower at Watch of that artist has no new_concerts notification row for it.
@spec-manual stories/get-notified-of-new-concerts "Browser gone" -- On prod after that release, register a browser for a test fan following at Away, then revoke the browser's notification permission so the push service returns 410. On the next organic fan-out for that artist, confirm that the fan's notification row is Failed and that the browser's push subscription row is deleted.
