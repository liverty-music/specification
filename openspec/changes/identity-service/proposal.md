## Why

Three identity-provider credentials sit on two workloads that handle untrusted input:
- The event consumer holds `backend-app` (`ORG_USER_MANAGER`, every fan identity) and `fan-passkey-recovery` (`ORG_OWNER` on the product org). It processes external data: Gemini results and official-site pages.
- The admin console API holds `backend-app` and `organizer-provisioner`.

`fan-passkey-recovery-and-management` already recorded the consumer's `ORG_OWNER` key as a risk and named a dedicated workload as the fix.

The next change (#1228: our own verification email, verified from an app page) needs a synchronous email verification for a fan who may not be signed in. The fan API must not hold a credential for it (spec `identity-provider-credentials`), and a role-less key on the fan API was judged weaker than keeping every credential in one internal-only place.

## What Changes

- A new backend workload, the **identity service**, holds every identity-provider credential and makes every identity-provider management call the platform makes. It takes no traffic from outside the cluster.
- The event consumer and the admin console API lose their identity-provider credentials and call the identity service instead:
  - the consumer for the verification email at sign-up, the verification resend and the passkey registration link;
  - the admin console API for deleting a fan identity and for creating, provisioning, deactivating and deleting an Organizer's Organization.
- Each calling workload can reach only the identity-service operations it needs, and nothing else can reach the identity service.
- The identity service's liveness and readiness reflect only the process, because it has no database.
- New internal RPC packages `liverty_music.rpc.internal.<entity>.v1`, and the `rpc-design` naming rule gains the `internal` caller.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `components/infrastructure/backend/process/identity-provider-credentials`: only the identity service holds an identity-provider credential. The event consumer and the admin console API make their identity changes through it, and each reaches only the operations it uses.
- `components/infrastructure/backend/process/health-probes`: the identity service's liveness and readiness reflect only the process, not the database or the identity provider.

The entity operations behind these calls keep their promises, so their specs are unchanged:
- `User.SendVerification`
- `User.ResendVerification`
- `User.SendPasskeyRegistrationLink`
- `User.DeleteIdentity`
- the `Organization` operations

The usecases that call them (`UserUseCase.ReissueEmailVerification`, `SendPasskeyRecoveryLink`, `Delete`, the `OrganizerUseCase` provisioning methods) are unchanged too; only the implementation behind each entity interface moves.

## Impact

- **specification**: `proto/liverty_music/rpc/internal/user/v1` and `rpc/internal/organization/v1`, a Release, and the `rpc-design` skill rule for the `internal` caller.
- **backend**:
  - a new `identity` binary and image, with no database and an internal Connect listener per caller;
  - clients for the event consumer and the admin console API that replace the Zitadel clients behind `EmailVerifier`, `PasskeyRegistrationLinkIssuer`, `IdentityRemover` and `OrganizationRepository`;
  - the image in the build and release pipelines.
- **cloud-provisioning**:
  - an `identity` Deployment and Service (ClusterIP, no Gateway route);
  - the first NetworkPolicy in the cluster, limiting the identity service's ingress per port to its callers;
  - the three keys moved to an `identity-secrets` ExternalSecret and unmounted from `event-consumer` and `admin-console-api`;
  - the new image in the prod pin.
- **frontend**: none.
- **Out of scope**: fan email verification from an app page (#1228), which will add a fan-API listener and `VerifyEmail` on the identity service.
