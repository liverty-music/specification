## Context

`TimetableRoute.maybeCelebrate()` read the `postSignup.shown` flag (`'pending'` or `'pending-track'`) and removed it at once, then showed the celebration (or waited for the concert sheet). The sheet opens from `onCelebrationDismissed()` or `onDetailSheetClosed()`. Anything that ended the page between those moments lost the flag.

## Decisions

- Clear the flag in one place, `openPostSignupDialog()`, called when the route sets `showPostSignupDialog`. "Opened" means the route has handed the sheet to `post-signup-dialog`; a sheet with nothing to ask (`pickSteps()` empty) still spends the flag, because there is nothing to retry.
- While the flag is still stored, `maybeCelebrate()` can run again (each data arrival). It returns early when the celebration is already showing, when the dialog is open, or when the sheet is already waiting for the concert sheet (`postSignupAfterSheet`), so nothing repeats within one visit.
- Leaving the route mid-celebration (in-app navigation) now also replays the celebration on return, because the flag is kept. That is the same guarantee as closing the app.
- Interaction with frontend#855 (the install banner during the sequence): `PromptCoordinator.isPostSignupSurfaceOpen` is set and released exactly as before; this change does not touch it.

## Consent wording

The notice states what is true for both audiences: analytics are on from the start, they are linked to the account while the fan is signed in, and Settings turns them off. It does not use "anonymous" in either language.
