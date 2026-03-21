## 1. Cloud Provisioning — Remove autoVerifyEmail

- [x] 1.1 Delete `autoVerifyEmail` Action, `PRE_CREATION` TriggerAction, and `auto-verify-email.js` script from `src/zitadel/components/token-action.ts` and `src/zitadel/scripts/`
- [x] 1.2 Remove `autoVerifyEmailAction` and `preCreationTrigger` from `ActionsComponent` class outputs and public properties
- [x] 1.3 Run `make check` and verify Pulumi preview shows only the expected deletions

## 2. Cloud Provisioning — Zitadel Machine User

- [x] 2.1 Create a `MachineUserComponent` in `src/zitadel/components/machine-user.ts` that provisions a `zitadel.MachineUser` named `backend-app` with `ACCESS_TOKEN_TYPE_JWT`
- [x] 2.2 Generate a `zitadel.MachineKey` (`backend-app-key`) with `KEY_TYPE_JSON` for the Machine User
- [x] 2.3 Grant the Machine User `ORG_USER_MANAGER` role via `zitadel.OrgMember`
- [x] 2.4 Output the Machine Key `keyDetails` for storage in GCP Secret Manager (`zitadel-machine-key`)
- [x] 2.5 Wire the `MachineUserComponent` into the `Zitadel` orchestrator class in `src/zitadel/index.ts`
- [x] 2.6 Run `make check` and verify Pulumi preview

## 3. Cloud Provisioning — K8s Secret Sync

- [x] 3.1 Add an ExternalSecret resource to sync `zitadel-machine-key` from GCP Secret Manager to a K8s Secret
- [x] 3.2 Mount the K8s Secret as a file volume in the backend Deployment manifest
- [x] 3.3 Add `ZITADEL_MACHINE_KEY_PATH` environment variable to the backend container pointing to the mounted file
- [x] 3.4 Render Kustomize overlays and verify manifests

## 4. Specification — Proto Schema

- [x] 4.1 Add `ResendEmailVerification` RPC method to `UserService` in `proto/liverty_music/rpc/user/v1/user_service.proto`
- [x] 4.2 Define request/response messages for `ResendEmailVerification`
- [x] 4.3 Run `buf lint` and `buf breaking` to validate

## 5. Backend — Zitadel API Client

- [ ] 5.1 Add `zitadel-go/v3` dependency via `go get`
- [ ] 5.2 Add `ZitadelMachineKeyPath` field to both `ServerConfig` and `ConsumerConfig` in `pkg/config/config.go`
- [ ] 5.3 Create Zitadel client initialization in `internal/infrastructure/zitadel/` using `client.DefaultServiceUserAuthentication`
- [ ] 5.4 Define an `EmailVerifier` interface in `internal/usecase/` for sending and resending verification emails
- [ ] 5.5 Implement the `EmailVerifier` interface in `internal/infrastructure/zitadel/`
- [ ] 5.6 Wire the Zitadel client into DI in both `internal/di/provider.go` (API server) and `internal/di/consumer.go` (event consumer), handling nil case for local dev

## 6. Backend — NATS USER Stream and Event

- [ ] 6.1 Add `USER` stream configuration to `internal/infrastructure/messaging/streams.go`
- [ ] 6.2 Define `entity.SubjectUserCreated` constant and `USER.created` event payload struct in `internal/entity/`
- [ ] 6.3 Inject `message.Publisher` (Watermill) into `userUseCase` struct, following existing pattern in `concertCreationUseCase`
- [ ] 6.4 Publish `USER.created` event in `UserUseCase.Create()` after successful database persistence
- [ ] 6.5 Create consumer in `internal/adapter/event/user_consumer.go` that subscribes to `USER.created` and calls `EmailVerifier.SendVerification()`. Use `logging.Logger` for trace-ID-aware error logging (via `ctx` from `msg.Context()`)
- [ ] 6.6 Wire the consumer into `internal/di/consumer.go` and register handler in the Watermill Router

## 7. Backend — Resend Verification RPC

- [ ] 7.1 Implement `ResendEmailVerification` handler in `internal/adapter/rpc/user_handler.go`
- [ ] 7.2 Extract `external_id` from JWT claims and call `EmailVerifier.ResendVerification()`
- [ ] 7.3 Return `codes.FailedPrecondition` when email is already verified
- [ ] 7.4 Return `codes.ResourceExhausted` when rate limit exceeded (3 requests per 10 minutes per user)
- [ ] 7.5 Write unit tests for the handler and use case logic

## 8. Frontend — Settings Page

- [ ] 8.1 Add email verification status display (verified/not verified indicator) to Settings page
- [ ] 8.2 Add "Resend verification email" button visible only for unverified users
- [ ] 8.3 Connect button to `ResendEmailVerification` RPC call
- [ ] 8.4 Add success/error feedback and temporary disable on button click

## 9. Integration Testing

- [ ] 9.1 Test the full signup flow in dev environment: Passkey registration → user created with unverified email → verification email received
- [ ] 9.2 Test resend from Settings page
- [ ] 9.3 Test verification via Zitadel hosted UI → `email_verified` claim updates on next token refresh
