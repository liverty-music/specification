## Why

Liverty Music opens an Organizer's payout account at the payment provider the first time anyone in the organizer console reads it: `PayoutAccountService.Get` runs on every Home visit and on Settings, creates the account when there is none, and creates a fresh onboarding link on every call while the account is not active (#1176). Opening a member's console is not a request to be paid out, so accounts are opened for Organizers that never asked (the deactivated test Organizers `fan-test` and `fan-test-2` hold Restricted accounts this way), every read of the status makes a write call to the provider, and an Organizer with such an account can no longer be deleted.

## What Changes

- `PayoutAccountService.Get` only reads. It returns the stored account with its status refreshed from the provider, as today, and fails with NotFound when the Organizer has no payout account. It opens no account and creates no onboarding link. **BREAKING**: `GetResponse.onboarding_url` (field 2) is removed and reserved; a caller that relied on Get to open the account now receives NotFound.
- New `PayoutAccountService.StartOnboarding`: opens the Organizer's payout account when it has none (owner email as contact, stored pending) and returns a fresh onboarding link. It is the only call that opens an account or creates a link.
- Organizer console Home: an Organizer with no payout account shows the same 要対応 item as a pending one (入金口座の登録が終わっていません, 登録する, opening Settings at the payout account), not a load failure.
- Organizer console Settings: with no payout account, no status line; the explanation of what Stripe asks for and Stripe で登録する. Pending and restricted keep Stripe で登録を続ける. Both buttons call StartOnboarding and go to Stripe in the same tab (no new tab); Stripe's return and refresh addresses stay the console address configured today, which opens Home, where the 要対応 item shows while the account is not active.
- Clean-up in production: remove the payout account records of `fan-test` and `fan-test-2` and delete both Organizers; their provider accounts are kept, as Organizer Delete keeps provider records.

## Capabilities

### New Capabilities

- `components/usecase/payout-account/start-onboarding`: PayoutAccountUseCase.StartOnboarding, which opens the account when the Organizer has none and returns a fresh onboarding link.

### Modified Capabilities

- `components/usecase/payout-account/get`: Get reads the stored account only and fails with NotFound when there is none; the requirements that opened the account and returned a link are removed (Purpose edited directly). It relies on PayoutAccount.GetByOrganizerID, GetStatus and UpdateStatus, which are unchanged. PayoutAccount.Create, Upsert and CreateOnboardingLink move to StartOnboarding with their promises unchanged, so no entity operation spec changes; the PayoutAccount entity (its states and the rule that a new account starts pending) is unchanged.
- `components/adapter/organizer/api/rpc/payout-account`: Get passes NotFound through and returns no onboarding link; StartOnboarding is added behind the same audience gate (Purpose edited directly).
- `components/infrastructure/organizer/web/route/home`: the payout item also shows when the Organizer has no payout account.
- `components/infrastructure/organizer/web/route/settings`: the not-set-up state, StartOnboarding behind both buttons, same-tab hand-off, and the return through Home.

Unchanged and relied on: `components/usecase/settlement/release-due-settlements` already withholds a Settlement when the Organizer has no payout account; `components/usecase/organizer/delete` and `components/entity/organizer/delete` keep refusing an Organizer with a payout account record.

## Impact

- **specification**: `proto/liverty_music/rpc/organizer/payout_account/v1/payout_account_service.proto` (field removal and a new RPC; merged with the `buf skip breaking` label), Release, BSR generation.
- **backend**: `internal/usecase/payout_account_uc.go` (Get read-only, StartOnboarding), `internal/adapter/rpc/payout_account_handler.go`, their tests.
- **frontend**: `organizer/services/payout-account-client.ts`, Home (`organizer/model/home-model.ts`, `organizer/home/home-route.ts`), Settings (`organizer/settings/*`), the `settings.payout.*` copy.
- **cloud-provisioning**: none; `STRIPE_ONBOARDING_RETURN_URL` keeps `https://organizer.liverty-music.app/`.
- **Deploy order**: proto → backend → frontend. Between the backend and frontend deploys, the deployed console cannot start onboarding and shows a load failure for an Organizer without an account (design: Migration Plan); acceptable because the product has no real Organizers yet.
- **Production data**: two `payout_accounts` rows removed by a break-glass write the owner confirms at that time.
