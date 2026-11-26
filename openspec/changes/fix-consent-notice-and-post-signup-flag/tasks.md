## 1. Frontend (specs: settings "Consent notice makes no anonymity claim", post-signup-dialog "The post-signup sequence survives closing the app")

- [ ] 1.1 Reword `onboarding.consent.intro` in `ja` and `en` so it is true for guests and signed-in fans (analytics on from the start, linked to the account while signed in, off in Settings), and remove the same claim from the other places that make it. Verify with the test for "Consent notice makes no anonymity claim".
- [ ] 1.2 Clear the `postSignup.shown` flag when the post-signup dialog opens instead of when the celebration starts, and keep `maybeCelebrate()` from repeating while the flag is stored. Verify with the tests for "App closed during the celebration" and "App closed before the concert sheet closes", and that the existing celebration and dialog scenarios still pass.
- [ ] 1.3 After the merge and the release, check that the new frontend version is pinned and rolled out in production (read-only).
