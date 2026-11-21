## 1. frontend (components/infrastructure/organizer/web/global/hosted-login)

- [x] 1.1 Keep an address's Organization as the tab's pending pin and remember it only when the route guard admits the member to it (design.md D1, D2). Verify with the unit tests of `organizer/services/org-handle.ts` and `organizer/hooks/auth-hook.ts` and the functional e2e "a link whose sign-in never completes is not remembered", which fail on the code before the fix. Done in frontend#1079, released in frontend v1.171.0
- [ ] 1.2 Annotate the frontend tests with the new scenarios: `@spec components/infrastructure/organizer/web/global/hosted-login "Link to an Organizer that does not exist"` on the functional e2e and the org-handle unit test, and `"Failed link keeps the remembered Organization"` on the org-handle unit test. Verify with `python3 scripts/check-scenario-coverage.py` finding both scenarios on frontend `main`

## 2. cloud-provisioning (components/infrastructure/organizer/web/global/hosted-login)

- [ ] 2.1 The modified requirement carries the existing scenario "Sign-in screen asks for the email alone", which no test covers: the hosted login hides the suffix through the instance default label policy (`hideLoginNameSuffix`, `src/zitadel/index.ts`). Add `@spec-manual components/infrastructure/organizer/web/global/hosted-login "Sign-in screen asks for the email alone" -- <how it is checked>` next to that setting. Verify with `python3 scripts/check-scenario-coverage.py remember-organizer-after-sign-in` reporting every scenario covered

## 3. Close-out (specification)

- [ ] 3.1 Verify with the verify-before-archive skill (shipping evidence: frontend#1079 and frontend v1.171.0 in prod) and archive the change. Verify with `openspec validate --specs` and the archive PR's CI passing
