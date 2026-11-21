## 1. specification: proto comments (comment-only PR, then a patch release)

- [x] 1.1 In `rpc/checkout/v1/checkout_service.proto` (Start), `rpc/lottery_entry/v1/lottery_entry_service.proto` (AuthorizeCard) and `rpc/resale_entry/v1/resale_entry_service.proto` (AuthorizeCard), document INVALID_ARGUMENT for a ticket_count below 1 or above 10 and FAILED_PRECONDITION for a ticket_count above the event's per-account limit; verify `buf lint` and `buf breaking` pass in the PR's CI
- [x] 1.2 After the proto PR merges, publish a patch release and verify the `buf-release.yml` run succeeds

## 2. frontend: screens (merge and deploy before section 3)

- [x] 2.1 Checkout (`components/infrastructure/fan/web/route/checkout`): hold only a count from 1 to the per-account limit, stop reading Start's InvalidArgument as the limit, and on AuthorizeCard InvalidArgument return to the personal details step with the new message; verify unit tests annotated `@spec` for "Name or phone number refused" and "Count above the limit is not sent" pass and fail without the change
- [x] 2.2 Lottery entry (`components/infrastructure/fan/web/route/new-lottery-entry`): send only a count from 1 to the per-account limit, map AuthorizeCard InvalidArgument to the 本人確認 step with the new message and FailedPrecondition to the existing reasons, the per-account limit only when the held tickets plus the count exceed it, and otherwise a new "cannot enter now" message; verify unit tests annotated `@spec` for "Name or phone number refused", "Over the limit with held tickets", "Refused for another reason" and "Count above the limit is not sent" pass and fail without the change
- [x] 2.3 Resale entry (`components/infrastructure/fan/web/route/new-resale-entry`): send only a count from 1 to the limit minus the held tickets, map AuthorizeCard InvalidArgument to the personal details step with the new message; verify unit tests annotated `@spec` for "Name or phone number refused" and "Count above the limit is not sent" pass and fail without the change
- [x] 2.4 Add the ja and en text for the name or phone number refusal (all three screens) and for the lottery entry's "entry was not made and cannot be made now" refusal, in the voice of the neighbouring entry copy; verify the unit tests of 2.1 to 2.3 assert these keys and the locale tests pass
- [x] 2.5 Run the lottery entry flow with Playwright (`--workers=2`) against a local build with the AuthorizeCard RPC answering InvalidArgument, and verify the 本人確認 step shows the new message
- [x] 2.6 After merge, verify the frontend release is deployed to production (ArgoCD rollout of the new image)

## 3. backend: usecases (after section 2 is live in production)

- [x] 3.1 `ValidateTicketCount`: InvalidArgument for a count below 1, FailedPrecondition for a count above the event's per-account limit; update its doc comment and table test
- [x] 3.2 CheckoutUseCase.Start (`components/usecase/checkout/start`): update `# Possible errors`; verify usecase tests annotated `@spec` for "Count over the limit" (now FailedPrecondition) and "No tickets" pass
- [x] 3.3 LotteryEntryUseCase.AuthorizeCard (`components/usecase/lottery-entry/authorize-card`): update `# Possible errors`; verify the "Count over the limit" usecase test now expects FailedPrecondition and "Missing identity details" still expects InvalidArgument
- [x] 3.4 ResaleEntryUseCase.AuthorizeCard (`components/usecase/resale-entry/authorize-card`): update `# Possible errors`; verify usecase tests annotated `@spec` for "Count over the limit" and "Missing identity details" pass
- [x] 3.5 After merge, verify the backend release is deployed to production (ArgoCD rollout of the new image)

## 4. Close-out

- [x] 4.1 Update the sequence diagrams in the Purpose of `components/usecase/checkout/start` and `components/usecase/lottery-entry/authorize-card` (count above the limit: FailedPrecondition) in the archive commit; verify `openspec validate --specs` passes
