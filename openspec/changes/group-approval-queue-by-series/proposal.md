## Why

The approval-queue screen presents pending concerts as a flat table, so a 20-date tour
from the same artist appears as 20 separate rows with repeated Artist and Title columns.
This makes triage slow: a reviewer must scroll through identical context to find the
one row whose resolved venue needs attention. The approved-concerts screen already solves
this with artist → series grouping, and the same pattern should apply to the queue.

## What Changes

- The approval-queue UI groups `PendingConcert` rows by performing artist and then by
  title (which serves as the series proxy for staged concerts).
- Each series is a collapsible `<details>` element whose summary shows the series title,
  date count, and an unresolved-venue count so reviewers can prioritise without expanding.
- The Artist and Title columns are removed from the inner table and promoted to group
  headers, making the per-row data narrower and easier to scan.
- Per-row Approve and Reject (with reason) actions are preserved unchanged; no bulk
  series-level actions are introduced.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `concert-approval-queue`: The admin console UI requirement changes to require that
  pending concerts are displayed grouped by artist and then by series title, matching the
  approved-concerts grouping pattern.

## Impact

- **Frontend** (`admin/approval-queue/`): `approval-queue-route.ts`, `.html`, `.css` —
  grouping logic and template restructured; no RPC changes.
- **Backend / specification / proto**: no changes.
