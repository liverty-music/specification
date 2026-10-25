## 1. Backend

- [x] 1.1 Confirm no caller of the Gemini searchers branches on `Unauthenticated`; map HTTP 403 to PermissionDenied in `toAppErr` and update its tests
- [x] 1.2 Add `errorCode(err)` and send `error_code` on the failed `concert.search.completed` and `ticket_sale.search.completed`; update the event comments in `analytics_events.go`
- [x] 1.3 Tests: `search-new-concerts` "Search failed" and "Failure without a kind"; `discover-for-artist` "Search failed for a spent quota"
