## Why

Two guest-only defects. A guest who already followed artists and finished onboarding is shown the Welcome landing page every time they open `/` (the installed PWA's `start_url`), where a signed-in fan goes straight to the timetable (frontend#854). And the guest timetable lists concerts from months ago, because the guest read, `ConcertService.ListByArtists`, has no date bound and the client dropped `from` for guests (frontend#852).

## What Changes

- Welcome redirects a returning guest to the timetable: unauthenticated, onboarding complete, and still following at least one artist. A guest still in onboarding keeps free access to Welcome, and a guest with no follows (a signed-out fan, or a guest who tapped `[Log In]`, which discards the follows) still sees Welcome.
- The guest timetable applies the same lower bound as the signed-in one: the client cuts the `ListByArtists` result to the dates on or after the timetable's `from`. `ListByArtists` stays "past and upcoming" for its other callers.
- No proto or backend change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/route/welcome`: new requirement "Returning Guest Redirect".
- `components/infrastructure/fan/web/route/timetable`: new requirement "Guest timetable follows the same date lower bound" (an ADDED requirement, so it does not touch "Default today-onward timetable", which `globalize-venues` modifies).

## Impact

- frontend: `src/routes/welcome/welcome-route.ts` (`canLoad`), `src/services/concert-store.ts` (guest branches of `listFollowed` and `revalidateFollower`).
- Interaction with `globalize-venues`: that change stops sending the device's date as the default `from` and lets the server apply each Venue's own today. `ListByArtists` has no `from`, so once the default view sends none, the guest cut has no bound and past concerts come back for guests. `globalize-venues` must give the guest read a Venue-local lower bound (a `from`-less default on `ListByArtists`, as `ListFollowed` has) in the same release; until then this change is the guest rule.
