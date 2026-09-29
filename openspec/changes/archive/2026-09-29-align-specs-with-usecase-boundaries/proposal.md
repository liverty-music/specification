## Why

Five backend refactors (liverty-music/backend#516–#520) are merged on main (120bd90). #519 moved the ownership and active-Organizer checks, and the verification-email resend limit, from the RPC handlers into usecases. #520 stopped usecases from calling other usecases: a follow's first concert search and every notification delivery now run from an announced event instead of a direct call. Several main specs still name the old callers and describe the old failure handling, so they no longer match what ships. This change brings the specs back to shipped behavior. The code change it still needs is small: the unused OrganizerUseCase.GetByZitadelOrgID is deleted, and tests are marked with the scenarios they verify.

## What Changes

- A fan's new follow no longer starts the first concert search itself. The follow announcement triggers the new usecase method ConcertUseCase.SearchNewConcertsOnFirstFollow, which searches only a never-searched Artist. A failed announcement means no search on that follow; the daily search picks the Artist up. **BREAKING** (spec-level): an unreadable search history or a failed search is now retried instead of ignored.
- NotificationUseCase.Notify is now NotificationUseCase.Deliver, and it runs once per requested notification. The spec's main path already moved to `components/usecase/notification/deliver` in a direct commit.
- PushNotificationUseCase.NotifyNewConcerts and SalesPhaseAnnouncementUseCase.AnnounceDiscoveredPhase now request one notification per recipient instead of recording it themselves:
  - They fail only when a request cannot be made.
  - A request repeated within 2 minutes reaches the fan once.
  - A recording failure affects only that fan's notification, not the batch.
- The organizer-facing boundaries (Organizer, Lottery, PayoutOnboarding and organizer Concert services) resolve the caller through the new OrganizerUseCase.ResolveCaller. The organizer roster is read through the new OrganizerUseCase.ListOwnArtists. What callers see does not change.
- The fan-facing User boundary resolves the caller through the new UserUseCase.ResolveCaller. The resend limit (3 per 10 minutes per User) moves into the new UserUseCase.ResendEmailVerification. What callers see does not change.
- OrganizerUseCase.GetByZitadelOrgID is removed. It has no caller left.

## Capabilities

### New Capabilities

- `components/usecase/concert/search-new-concerts-on-first-follow`: starts the first concert search for a never-searched Artist when a new follow is announced, and retries on failure.
- `components/usecase/organizer/resolve-caller`: turns an operator's tenant into their own active Organizer. A missing or provisioning Organizer gives PermissionDenied; a deactivated one gives FailedPrecondition.
- `components/usecase/organizer/list-own-artists`: the caller's own roster, or PermissionDenied for any other Organizer.
- `components/usecase/user/resolve-caller`: the caller's User, or InvalidArgument, PermissionDenied or NotFound.
- `components/usecase/user/resend-email-verification`: resends the caller's verification email, at most 3 per 10 minutes per User.

### Modified Capabilities

- `components/usecase/follow/follow`: "Follow announces the new follow" now states that the announcement triggers the first search. "First concert search started in the background" is removed. (Purpose) edited directly.
- `components/usecase/notification/deliver`: every requirement names Deliver. Adds "Runs for each requested notification". (Purpose) and title edited directly with the move from `notification/notify`.
- `components/usecase/notification/notify-new-concerts`: "One new_concerts notification per matched follower" is removed. It is replaced by "One new_concerts notification requested per matched follower", which covers per-follower requests, request failure and the 2-minute repeat.
- `components/usecase/sales-phase/announce-discovered-phase`: "One sales-phase announcement notification per recipient" is removed. It is replaced by "One sales-phase announcement notification requested per recipient".
- `components/usecase/organizer/get-by-zitadel-org-id`: its only requirement is removed.
- `components/usecase/organizer/list-artists`: (Purpose) only, edited directly. It is admin-only and has no ownership check.
- `components/usecase/concert/search-new-concerts`: (Purpose) only, edited directly. It is also run on an Artist's first follow.
- `components/adapter/organizer/api/rpc/organizer`: the caller is resolved through ResolveCaller and ListArtists goes through ListOwnArtists.
- `components/adapter/organizer/api/rpc/lottery`, `components/adapter/organizer/api/rpc/payout-onboarding`, `components/adapter/organizer/api/rpc/concert`: the caller is resolved through ResolveCaller.
- `components/adapter/fan/api/rpc/user`: "Per-user calls act only on the caller's own account" resolves the caller through UserUseCase.ResolveCaller. "Resending the caller's verification email" is removed. It is replaced by "ResendEmailVerification is decided by the usecase", and its limit scenarios move to `components/usecase/user/resend-email-verification`.
- `stories/follow-an-artist`: the first search is started on the follow announcement. Adds the "Follow not announced" scenario.
- `stories/get-notified-of-new-concerts`: the notifications are recorded and pushed by NotificationUseCase.Deliver.

Entities and entity operations used by these usecases, all unchanged:
- SearchLog.GetByArtistID.
- Organizer.GetByZitadelOrgID, Organizer.Get, Organizer.ListArtists.
- User.GetByExternalID, User.ResendVerification.
- Notification.Create, Notification.UpdateDelivery.
- PushSubscription.ListByUserIDs, PushSubscription.Send, PushSubscription.Delete.

## Impact

- backend:
  - Delete OrganizerUseCase.GetByZitadelOrgID from the usecase interface and its implementation, and regenerate the mocks. The entity operation Organizer.GetByZitadelOrgID stays, because ResolveCaller uses it.
  - Add `@spec` annotations (and the missing tests) for every added or modified scenario. No other behavior change.
- No proto, frontend or infrastructure changes.
