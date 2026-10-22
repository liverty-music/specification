## Context

See proposal.md - Why. Verified state on 2026-10-22:

- One backend binary starts three Connect listeners: fan, admin and organizer (`backend/internal/di/provider.go:700-760`). Each Deployment routes only its own port. The `fan-api` Pod therefore also runs the admin listener in process, but it is unrouted.
- DI builds two clients whenever `ZITADEL_MACHINE_KEY_FOR_BACKEND_APP_PATH` is set (`provider.go:258-275`):
  - `EmailVerifier` (Send/ResendVerification).
  - `IdentityRemover` (DeleteIdentity).
- The `backend-app` key is mounted on `fan-api` (`cloud-provisioning/k8s/namespaces/backend/base/fan-api/external-secret.yaml:27-29`), `event-consumer` (`event-consumer/deployment.yaml:33-38`) and `admin-console-api` (`admin-console-api/deployment.yaml:30-35`).
- Uses of the key:
  - `SendVerification`: event consumer, on `USER.created` (`internal/adapter/event/user_consumer.go:54`).
  - `ResendVerification`: fan RPC through `UserUseCase.ResendEmailVerification` (`internal/usecase/user_uc.go:427-440`).
  - `DeleteIdentity`: `UserUseCase.Delete`, which only the admin UserService exposes (spec `components/usecase/user/delete`). Delete already returns early when the remover is nil (`user_uc.go:369-371`).
- `backend-app` holds `ORG_USER_MANAGER` on the product org (`cloud-provisioning/src/zitadel/components/machine-user.ts:94`), which includes `user.write` and `user.delete` over every fan (`zitadel cmd/defaults.yaml:1941-1959`).

During exploration, best practice for removing a standing all-users credential from an internet-facing service was checked (RFC 9700 §2.3, ASVS 5.0 8.3.3, OWASP Identity Propagation Patterns, NIST SP 800-207A/204B, draft-ietf-oauth-transaction-tokens-11). Those sources matter for an operation a fan triggers on their own identity. The only such operation here is a verification resend, and its effect cannot hurt the fan even if forged. That makes the simplest pattern sufficient.

## Goals / Non-Goals

**Goals:**
- The `fan-api` Pod has no identity-provider management credential.
- The fan-facing behaviour of the resend stays as it is on screen.

**Non-Goals:**
- Fan self-service account deletion. It does not exist today, and no fan surface calls `UserUseCase.Delete`. If it is added later, it should run the identity provider's self-deletion with the fan's own freshly re-authenticated token (ZITADEL self-deletion guide; ASVS 8.3.3), not through a service account.
- Moving the key off `event-consumer` or `admin-console-api`.
- Splitting the binary so the fan Pod stops running the admin and organizer listeners.

## Decisions

### D1. Resend becomes an announcement handled by the event consumer

`UserUseCase.ResendEmailVerification` keeps its limiter (3 per 10 min per User, counted after the caller is resolved). It then publishes `USER.email_verification_resend_requested` with `{user_id}` and returns.

A new consumer handler `reissue-email-verification` runs `UserUseCase.ReissueEmailVerification`:
1. `User.Get`.
2. `User.ResendVerification` with the existing `EmailVerifier`.
3. On FailedPrecondition (already verified) or NotFound, finish.
4. If the verifier is not configured, log and finish.
5. On anything else, return the error so the message is redelivered.

Why this is safe: a forged announcement can only make the identity provider send a code to the identity's own registered address. It cannot change an identity. The same reasoning is applied to recovery links in `fan-passkey-recovery-and-management` D1.

Alternatives:

| Alternative | Rejected because |
|---|---|
| The SPA calls the identity provider's `ResendEmailCode` with the fan's own token | Every Settings visit would need a token carrying the identity provider's audience, which widens XSS exposure. That is out of proportion for a resend. |
| Keep the key on `fan-api` with a narrower custom role | ZITADEL role mappings can only be replaced as a whole list, and there is no narrower built-in role (see `fan-passkey-recovery-and-management` D2). |

### D2. Observable change: already-verified and unconfigured are no longer caller errors

The fan API can no longer ask the identity provider whether the address is verified, so it cannot return FailedPrecondition. The Settings page shows the resend button only while the token says the address is unverified (spec `route/settings`, "Guest-Adaptive Account Section"). In practice the only difference is a race with verification in another tab, which now shows "Sent" instead of an error.

"Not configured" was a local-development case: there is no key in `make dev`. It is now logged by the consumer.

### D3. Remove the mount from `fan-api` only

Remove the `zitadel-machine-key-for-backend-app.json` entry from `fan-api/external-secret.yaml` and remove its volume and mount. With the path unset, DI builds neither client in the `fan-api` Pod:
- The unrouted in-process admin `Delete` gets a nil remover and returns early.
- The resend no longer uses the verifier.

Keep the key in `backend-secrets` for `event-consumer` and `admin-console-api`. Add a startup log line that states which identity-provider clients were built, so the absence is visible in `fan-api` logs.

## Risks / Trade-offs

- **[Risk]** If the consumer is scaled to zero, the KEDA cold start (`pollingInterval: 30`) delays the resend email by up to about 1 minute. → The UI already says "Sent" and does not promise immediacy. Add the KEDA trigger so the consumer wakes on the new subject.
- **[Risk]** A redelivered announcement sends a second code. → This is harmless, and the newer code wins.
- **[Trade-off]** Callers lose the FailedPrecondition signal (D2).
- **[Residual]** `event-consumer` and `admin-console-api` still hold `user.write` and `user.delete` over every fan. Neither takes fan traffic from the internet. The admin console API is behind admin sign-in, and the event consumer has no inbound internet traffic.

## Migration Plan

1. **backend**: ship the announce-and-consume resend, with tests. Deploy while `fan-api` still mounts the key: the behaviour already uses the consumer, so this step changes nothing for users.
2. **cloud-provisioning**:
   - Add the KEDA trigger for `reissue-email-verification`.
   - Remove the key from `fan-api`'s ExternalSecret and Deployment.
   - Merge, then roll out to prod.
3. **Verify in prod** (dev is stopped):
   - `kubectl exec` into `fan-api` shows no `/secrets/zitadel`.
   - `fan-api` startup logs show no identity-provider clients.
   - With the owner account, a resend from Settings on an unverified test address delivers a code. If no unverified account exists, use a consumer unit test plus a prod log line of a handled request.

**Rollback**: re-add the mount. The consumer path keeps working either way.
