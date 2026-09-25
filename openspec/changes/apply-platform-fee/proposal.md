## Why

`components/entity/order/issue` and `components/usecase/order/issue-from-captured-win` both describe the Held Settlement created at issuance with the platform fee left as `TODO(threshold)` (or, in the usecase spec, omitted entirely — the Organizer's split is currently the Order's full amount). The business has now decided the rate (specification#778): a flat 5% of the Order's amount. This change numbers the threshold and makes the Organizer's split net of that fee.

## What Changes

- The platform fee is a flat 5% of the Order's amount, rounded down to the nearest whole yen (`floor(amount × 5 ÷ 100)`, integer arithmetic). The Organizer's split absorbs the rounding remainder, not the platform.
- `Order.Issue`'s Held Settlement pays the Organizer the Order's amount minus this fee, replacing the `TODO(threshold)` placeholder.
- `IssuanceUseCase.IssueFromCapturedWin`'s Held Settlement split is updated to match: previously it paid the Organizer the Order's full amount (no fee deducted); it now deducts the same flat 5% fee.
- For very small amounts (under 20 yen at 5%) the fee rounds down to 0 and the Organizer receives the full amount as their split; this still satisfies the existing Settlement split invariants (every split greater than 0, sum of splits no greater than the Order's amount).

## Capabilities

### Modified Capabilities

- `components/entity/settlement`: adds the platform fee rate requirement (flat 5%, rounded down) and refreshes the "Splits and platform fee" requirement's example to use consistent numbers.
- `components/entity/order/issue`: replaces the `TODO(threshold)` placeholder with the concrete fee rule.
- `components/usecase/order/issue-from-captured-win`: the Held Settlement's split now nets out the platform fee instead of paying the Organizer the Order's full amount.

No other spec needs a change for this decision: `components/entity/settlement/create-transfer`, `reverse-transfer`, `mark-released`, `components/usecase/settlement/release-due-settlements`, `components/entity/order/commit-refund` and `components/usecase/order/refund-order` all operate on whatever split amounts a Settlement already carries — they never compute or restate the fee — so paying/reversing/releasing a smaller Organizer split needs no wording change there.

## Impact

- Backend: `internal/usecase/issuance_uc.go` (the `TODO(threshold)` comment and the Organizer split computation), plus a new named fee formula near the Settlement entity (`internal/entity/settlement.go`).
- No proto/RPC surface change — the fee is derived server-side, not a new field.
- External: business decision already made (specification#778); no further legal/compliance dependency.
