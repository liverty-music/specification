## 1. frontend

- [x] 1.1 In `welcome-route.ts` `canLoad`, send an unauthenticated guest whose onboarding is complete and who follows at least one artist to the timetable; verify one unit test per scenario of `route/welcome` "Returning Guest Redirect"
- [x] 1.2 In `concert-store.ts`, cut the guest `listFollowed` and `revalidateFollower` result to the dates on or after `from`; verify one unit test per scenario of `route/timetable` "Guest timetable follows the same date lower bound"
- [x] 1.3 Read-only production check after the release: the pinned frontend version is the merged one and the rollout is complete
- [x] 1.4 Spec only: state in `route/notifications` "Only a signed-in fan can open the center" that a returning guest goes on from `/welcome` to the timetable; verify the test of its scenario "Guest" on frontend `main`

## 2. Dependency on globalize-venues (not a task of this change)

`ListByArtists` has no `from`, and `globalize-venues` makes the default timetable send none. Its owner must add the guest read's Venue-local lower bound (a `ListByArtists` delta and a proto task) before its time release; until then the client cut of this change is the guest rule. Recorded in the proposal's Impact and in the pull request of this change.
