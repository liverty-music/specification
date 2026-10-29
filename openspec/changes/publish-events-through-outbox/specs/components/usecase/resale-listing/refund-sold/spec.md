## REMOVED Requirements

### Requirement: Refund announced
**Reason**: ResaleListing.RecordRefund announces the refund together with recording it (components/entity/resale-listing/record-refund), and every recorded announcement is delivered (components/infrastructure/backend/process/event-delivery), so RefundSold no longer announces, and no longer announces again until the sold email is sent.
**Migration**: The sold email runs from RecordRefund's announcement; a failed email is retried by its own delivery, not by RefundSold. ListSoldUnrefunded stops returning refunded listings whose email is not sent.
