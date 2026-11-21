## Context

See proposal.md (Why) for the problem. Today one entity check, `ValidateTicketCount` in the backend entity layer, refuses a count below 1 or above the event's per-account limit with InvalidArgument, and CheckoutUseCase.Start, LotteryEntryUseCase.AuthorizeCard and ResaleEntryUseCase.AuthorizeCard return it unchanged. The two AuthorizeCard methods also refuse missing or malformed personal details with InvalidArgument. The RPC boundary (protovalidate) refuses a `ticket_count` outside 1 to 10 with InvalidArgument before any usecase runs.

On the screens, the lottery entry and resale entry screens read InvalidArgument from AuthorizeCard as a refusal of the application (frontend#1077), and the checkout reads InvalidArgument from Start as the per-account limit. The checkout's AuthorizeCard has no count, so its InvalidArgument is always the personal details, but the screen shows only a generic retry message for it.

The per-account limit of a published event cannot change (Series.Update refuses it with FailedPrecondition), and every screen here reads the limit from TicketSaleService.ListByEvent (`per_account_limit`). So the limit a screen knows is the limit the server checks.

## Goals / Non-Goals

**Goals:**
- One meaning per code for these three calls: InvalidArgument is the request itself (a count below 1, personal details), FailedPrecondition is the event or the fan's holdings.
- Ship without a window in which a screen misreads a code, given that each merge deploys to production.

**Non-Goals:**
- Error details (`google.rpc.ErrorInfo`) that name the reason. The screens already re-read state to tell FailedPrecondition reasons apart; a reason field would be a second mechanism for the same job.
- The organizer's per-account limit setting (Event's rule, 1 to 10): an out-of-range setting stays InvalidArgument.
- Confirm of the lottery and resale entries: its InvalidArgument is the amount not matching, unrelated to this change.

## Decisions

### 1. Split the count check by what it depends on

`ValidateTicketCount` returns InvalidArgument for a count below 1 and FailedPrecondition for a count above the event's limit. A count above 10 never reaches a usecase (the boundary refuses it with InvalidArgument), so the usecase needs no third branch for it.

Alternative: return a reason in an error detail and keep InvalidArgument. Rejected: the code would still contradict the gRPC definition of INVALID_ARGUMENT ("problematic regardless of the state of the system"), and every client would need a detail parser.

### 2. The screens check the count before sending it

Each screen sends only a count from 1 to the per-account limit it read (the resale entry screen: minus the tickets the fan holds, which it already offers). With that check in place, an InvalidArgument from AuthorizeCard can only be the personal details, from the old backend and from the new one alike, so the screen needs no branch on which backend answered. A FailedPrecondition keeps the existing re-read and reasons.

The checkout's Start no longer reads InvalidArgument as the limit: after the count check, the old backend returns InvalidArgument from Start for no count the screen sends, so an InvalidArgument there is unexpected and is logged and shown as a retryable error (frontend AGENTS.md, review criterion on ConnectError).

### 3. The new message names the fields, not the rule

On InvalidArgument the screen returns to the personal details step, keeps what the fan typed and asks them to check the name and phone number. The screen's own checks (a non-blank name, a phone number that converts to E.164) already pass at that point, so the refusal is for a rule the screen's form does not check, such as a name over 200 characters; the app's request validation (the same protovalidate rules, run before sending) also fails such a request with InvalidArgument, and it is handled the same way. The message does not try to say which field.

### 4. Rollout order

1. Plan PR (this change) and a comment-only proto PR in specification, then a patch release so the BSR documentation matches. The generated types do not change, so frontend and backend do not wait for BSR generation.
2. Frontend PR: merged and deployed first. It is correct against the current backend (decision 2).
3. Backend PR: merged after the frontend is live in production. From then on Start and the two AuthorizeCard methods return FailedPrecondition for a count above the limit.

Rollback: reverting the backend PR restores InvalidArgument, which the new frontend still handles (decision 2). Reverting the frontend while the new backend runs would bring back #1077's wrong message for personal details only; the count case would show the per-account limit through FailedPrecondition, which the old frontend already maps.

## Risks / Trade-offs

- [A client other than this frontend reads InvalidArgument as the limit] → None exists; the proto comments document the new codes.
- [The screen's limit is stale] → The limit of a published event cannot change, and the screen reads it when it opens.
