## Why

The `rpc-auth-scoping` capability (introduced by `standardize-user-scoped-rpc-auth`) now defines a project-wide convention: every authenticated per-user RPC SHALL carry an explicit `entity.v1.UserId` field and the handler SHALL verify it matches the JWT-derived userID via the shared `requireMatchingUserID` helper. The ticket system's RPCs (`MintTicket`, `ListTickets`, `GetMerklePath`) predate this convention and were deliberately designed with `reserved "user_id"` on the request messages, identifying the caller from the JWT alone. This leaves the ticket/entry surface as the only authenticated per-user RPCs that violate the cross-service standard. Aligning them now — before the `implement-ticket-system-mvp` change is archived — keeps the `ticket-management` and `zkp-entry` specs coherent with `rpc-auth-scoping` when they enter `specs/` and avoids a later breaking migration once external clients start depending on the MVP shape.

## What Changes

- **BREAKING**: `MintTicketRequest` gains a required `user_id` field (replaces the current `reserved 2 / reserved "user_id"`). The backend SHALL verify it matches the JWT-derived userID; mismatches return `PERMISSION_DENIED`.
- **BREAKING**: `ListTicketsRequest` gains a required `user_id` field (replaces the current `reserved 1 / reserved "user_id"`). The backend SHALL verify it matches the JWT-derived userID; mismatches return `PERMISSION_DENIED`.
- **BREAKING**: `GetMerklePathRequest` gains a required `user_id` field (replaces the current `reserved 2 / reserved "user_id"`). The backend SHALL verify it matches the JWT-derived userID; mismatches return `PERMISSION_DENIED`.
- `GetTicketRequest` and `VerifyEntryRequest` remain unchanged — `GetTicket` is keyed by `ticket_id` (not user-scoped at the request boundary) and `VerifyEntry` is explicitly unauthenticated (the ZK proof itself is the authentication).
- Backend: `ticket_handler.go` call sites for the three affected RPCs SHALL delegate the check to the existing shared helper `mapper.RequireUserIDMatch`, following the same pattern used by `UserHandler` today.
- Frontend: every call site of the three affected RPCs SHALL inject the cached `user_id` from the `localStorage` cache introduced by `standardize-user-scoped-rpc-auth`.

## Capabilities

### New Capabilities
<!-- None. The target capabilities (ticket-management, zkp-entry) are introduced by the parallel `implement-ticket-system-mvp` change; this change only amends their deltas before archiving. -->

### Modified Capabilities
- `ticket-management`: The `MintTicket` and `ListTickets` request requirements change to include the explicit `user_id` field and the JWT-match check. The "user identified from JWT claims" scenarios are replaced with "user_id supplied, JWT-match enforced" scenarios.
- `zkp-entry`: The `GetMerklePath` request requirement changes to include the explicit `user_id` field and the JWT-match check. `VerifyEntry` is explicitly noted as exempt (unauthenticated by design).

## Impact

- **Proto (specification repo)**: Breaking changes to three request messages (`ticket/v1/ticket_service.proto`, `entry/v1/entry_service.proto`). `buf skip breaking` label required on the PR. No external consumers on `buf.build/liverty-music/schema` today other than this monorepo's backend and frontend, so the breaking change is contained.
- **Backend**: `ticket_handler.go` updates for the three RPCs. Handler-level tests expand to cover `PERMISSION_DENIED` paths. No changes to `ticket_uc.go` or the repository layer — the check lives entirely in the adapter layer.
- **Frontend**: Ticket RPC call sites inject the cached `user_id`. The `user_id` cache infrastructure already exists from `standardize-user-scoped-rpc-auth`; this change is additive.
- **Database**: No schema change.
- **Release sequence**: Specification PR → GitHub Release (new minor version, marked breaking) → BSR gen completes → backend + frontend PRs land. Follows the workspace's standard cross-repo release coordination.
- **Dependency on `implement-ticket-system-mvp`**: This change SHOULD merge and deploy **before** `implement-ticket-system-mvp` is archived, so the capability specs that land in `openspec/specs/ticket-management/` and `openspec/specs/zkp-entry/` already reflect the `rpc-auth-scoping` convention rather than requiring an immediate corrective delta.
