## Why

Two fan-facing promises are wrong today. The onboarding consent notice calls the analytics "anonymous", but a signed-in fan's analytics are tied to their account (`identify(userId)`), and the Settings requirement already forbids the word for that reason (frontend#888). The one-shot flag that schedules the post-signup sheet is spent when the celebration appears, so a fan who closes the app during the celebration never gets the sheet that asks for notifications and install (frontend#885).

## What Changes

- The consent notice's introduction no longer says the analytics are anonymous. It says the analytics are on from the start, that they are linked to the account while the fan is signed in, and that Settings turns them off. The rule that Settings already follows now covers the notice.
- The post-signup one-shot flag is cleared when the post-signup sheet opens, not when the celebration starts. Closing the app during the celebration, or while the sheet that precedes the notification step is still open, leaves the flag in place and the sequence runs on the next visit.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/route/settings`: MODIFIED requirement "Consent toggles invite the fan to help, in plain words" gains a scenario saying the onboarding consent notice makes no anonymity claim either.
- `components/infrastructure/fan/web/global/celebration-overlay`: MODIFIED requirement "Two-Tier Celebration Overlay" says when the post-signup tier counts as shown, and its scenario "Celebration does not replay" follows that.
- `components/infrastructure/fan/web/global/post-signup-dialog`: ADDED requirement "The post-signup sequence survives closing the app", with scenarios for the celebration and for the concert sheet.

## Impact

Frontend only: `src/locales/{ja,en}/translation.json` (`onboarding.consent.intro`), `src/routes/timetable/timetable-route.ts` and their tests. Issue frontend#855 (celebration and the install banner) is a separate fix and is not changed here.
