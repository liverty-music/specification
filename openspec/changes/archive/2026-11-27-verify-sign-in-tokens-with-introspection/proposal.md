## Why

The fan, admin console and organizer APIs accept any unexpired token the sign-in service signed that names an identity and an email address. An ID token, which lives 12 hours and is not meant for calling an API, passes as the 30-minute access token, and the fan and admin console APIs also accept tokens issued for another app.

## What Changes

- **BREAKING** The fan, admin console and organizer APIs accept only an access token that the sign-in service reports active. An ID token, a revoked token and a token of a removed identity are refused with Unauthenticated.
- **BREAKING** A token issued for another app is refused with PermissionDenied by every one of the three APIs.
- An answer from the sign-in service is reused for at most 60 seconds. While it cannot be asked, a call that needs a sign-in fails with Unavailable, not Unauthenticated, so no app signs the person out.
- The record of a removed identity is forgotten 90 seconds after the identity is removed, instead of being kept for good.
- Each of the three APIs holds a key that only lets it ask whether a token is valid.
- Every backend call to the sign-in service goes over the cluster network instead of the public load balancer.
- Names and a description that still call the workflow worker the event consumer are corrected.

The apps already send access tokens, so no screen changes. The reception API takes no sign-in and is unchanged.

## Capabilities

### New Capabilities

- `components/adapter/fan/api/rpc/sign-in`: which sign-in the fan API accepts.
- `components/adapter/admin/api/rpc/sign-in`: which sign-in the admin console API accepts.
- `components/adapter/organizer/api/rpc/sign-in`: which sign-in the organizer API accepts.
- `components/entity/user/forget-removed-identity`: removes the record of a removed identity.

### Modified Capabilities

- `components/entity/user/create`: refuses a removed identity while its removal is recorded.
- `components/entity/user/delete`: the record lasts until it is forgotten.
- `components/usecase/user/delete`: forgets the record after the identity is removed.
- `components/infrastructure/backend/process/identity-provider-credentials`: the APIs may hold a key for asking about tokens.

`components/adapter/organizer/api/rpc/organizer` already refuses a sign-in not issued for the organizer console with PermissionDenied and is unchanged, as are `components/usecase/user/create` and `components/infrastructure/backend/process/startup-dependencies`.

## Impact

- backend: token authentication of the three APIs, every sign-in service client, the `delete-user` removal and one new workflow, configuration.
- cloud-provisioning: one API application and key in each of three Zitadel projects (a prod `pulumi up` by the owner), secrets, manifests.
- No proto, database schema or frontend change.
