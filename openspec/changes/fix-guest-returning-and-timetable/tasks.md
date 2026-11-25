## 1. frontend

- [ ] 1.1 In `welcome-route.ts` `canLoad`, send an unauthenticated guest whose onboarding is complete and who follows at least one artist to the timetable; verify one unit test per scenario of `route/welcome` "Returning Guest Redirect"
- [ ] 1.2 In `concert-store.ts`, cut the guest `listFollowed` and `revalidateFollower` result to the dates on or after `from`; verify one unit test per scenario of `route/timetable` "Guest timetable follows the same date lower bound"
- [ ] 1.3 Read-only production check after the release: the pinned frontend version is the merged one and the rollout is complete

## 2. specification

- [ ] 2.1 When `globalize-venues` lands, give the guest read a Venue-local default lower bound so the guest timetable still hides past concerts without a device date (see proposal, Impact)
