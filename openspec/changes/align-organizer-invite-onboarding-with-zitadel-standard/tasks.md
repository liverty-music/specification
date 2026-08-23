## 1. Backend — standard invite + login policy (organizer-accounts)

- [x] 1.1 Change the provisioner `CreateInviteCode` `url_template` to the Zitadel
  standard `/verify` form — `https://auth.{base}/ui/v2/login/verify?code={{.Code}}&userId={{.UserID}}&organization={{.OrgID}}&invite=true` — deriving `auth.{base}` from the issuer; remove the console-pointed `url_template` and the `login_hint`/`org_id` baking (design D-A)
- [x] 1.2 Set the tenant login policy `default_redirect_uri = https://organizer.{base}/?org_id=<tenantOrgId>` in `ensureLoginPolicy` on BOTH the `AddCustomLoginPolicy` (create) and `UpdateCustomLoginPolicy` (converge existing) paths; the `org_id` lets the console enforce the authenticated org (design D-B + D-D Option 2)
- [x] 1.3 Keep `allowUsernamePassword=true` (shipped v1.39.0); ensure the Update path converges existing tenant orgs to include the new `default_redirect_uri` (design D-C)
- [x] 1.4 Unit tests: `url_template` points at `auth.{base}/…/verify`, contains `{{.Code}}`/`{{.UserID}}`, and carries no console origin; login-policy request includes the console `default_redirect_uri`
- [x] 1.5 `make check` passes

## 2. Frontend — enforce the authenticated org, land via default redirect (organizer-console)

- [x] 2.1 After the OIDC callback, enforce the token's org equals the URL `org_id` (carried by `default_redirect_uri`, design D-D Option 2); on match proceed to `/welcome`, on mismatch sign the stale session out and re-sign-in with `prompt=login` (+ `org:id` pin) so the operator authenticates as the correct tenant
- [x] 2.2 Handle the `default_redirect_uri` landing: read `org_id` from the URL, pin the `org:id` scope on the OIDC request, and complete sign-in to `/welcome`
- [x] 2.3 Retire the now-optional `login_hint` first-time onboarding handling (no operator flow depends on it); keep only if useful as a plain pre-fill
- [x] 2.4 Unit tests for the org-enforcement branch (match → welcome; mismatch → re-auth/sign-out) and the default-redirect landing
- [x] 2.5 `make check` passes

## 3. Ship + verify end-to-end (clean session, fresh operator)

- [ ] 3.1 Release backend and frontend to prod
- [ ] 3.2 E2E on a fresh operator in a clean (incognito) session: exactly ONE "Accept invite" email → click → passkey → `/welcome`; confirm from Zitadel logs that the login-app `CreateInviteCode` fired once (no second email) — validates the design's not-yet-verified single-email claim
- [ ] 3.3 Security check: enter the console with a pre-existing DIFFERENT-org Zitadel session in the browser → confirm the operator is NOT silently onboarded as the other org (forced re-auth / rejection)
- [ ] 3.4 Confirm the console origin passes Login v2 `isSafeRedirectUri` for `default_redirect_uri` (else fall back to the `DEFAULT_REDIRECT_URI` env override)

## 4. Reconcile prior records

- [ ] 4.1 Correct the archived organizer-console design D7 and tracking issue liverty-music/specification#843: the duplicate invite emails were caused by TWO OIDC authorize flows (each sending one invite), NOT by "/verify re-firing on every render"
- [ ] 4.2 File/track the independent Zitadel notification defect (`could not set notification event on aggregate: Errors.User.NotFound` for tenant-org operators) separately — out of scope for this change
