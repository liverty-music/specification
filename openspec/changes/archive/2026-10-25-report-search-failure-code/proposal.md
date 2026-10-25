## Why

A failed concert or ticket-sale search reports only `outcome: failed`. PostHog cannot tell a spent Gemini quota from a timeout or a broken official site. On the manual prod run of 2026-10-24, 6 of 17 searches failed, 5 on a spent spend cap and 1 on a timeout, and only the pod logs showed which (backend#704). A spent cap also surfaced as `unauthenticated`, which points at the API key.

## What Changes

- The "concert search completed" and "ticket sale search completed" signals of a failed search carry the kind of error that failed it, e.g. `deadline_exceeded`, `unavailable` or `permission_denied`. The error message is not sent: it can quote page content.
- Gemini's HTTP 403 maps to PermissionDenied instead of Unauthenticated, so a spent spend cap no longer reads as a credentials problem. 401 stays Unauthenticated and is still retried.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/usecase/concert/search-new-concerts`: "Each search reports its outcome" adds the error kind of a failed search.
- `components/usecase/ticket-sale/discover-for-artist`: "Each search reports its outcome" adds the error kind of a failed search.

## Impact

- backend: `internal/usecase/concert_uc.go` (`executeSearch`), `internal/usecase/ticket_sale_discovery_uc.go` (`reportSearch`), `internal/usecase/analytics_events.go` (event comments), `internal/infrastructure/gcp/gemini/errors.go` (`toAppErr`) and their tests.
- No proto, schema or infrastructure change. Existing PostHog insights keep working: `error_code` is a new property, present only on failed searches.
