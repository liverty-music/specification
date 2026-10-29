## MODIFIED Requirements

### Requirement: Refund within one minute after the sale

RefundSold SHALL take a ResaleListing and run once for each listing that Order.Issue makes Sold, started from the announcement of that sale. It SHALL resolve the charge of the listing's Order with Order.GetProviderChargeID, refund the listing's refund amount of that charge with Order.CreateRefund for the purpose of this listing, and record it with ResaleListing.RecordRefund. A listing that already has a refund time SHALL be left as it is; a run again refunds at most once. When a step fails with Unavailable it SHALL try again until 24 hours after the run started; a run that ends with a failure, or stops at its 24 hours, SHALL be reported to an admin with the listing's id and its Order's id.

#### Scenario: Ticket resold
- **WHEN** a won resale entry's Order is issued at 18:20 with a listing priced 5000 yen
- **THEN** right after 18:20 the listing's user is refunded 4500 yen on the card they paid with, and the refund is recorded

#### Scenario: Refund fails once
- **WHEN** the refund of one listing fails with Unavailable
- **THEN** the refunds of the other listings are not delayed and the failed one is tried again

#### Scenario: Refunded but not recorded
- **WHEN** a refund was issued and recording it failed
- **THEN** the run again records the same refund and the user is not refunded twice

#### Scenario: Charge cannot be refunded
- **WHEN** a listing's refund keeps failing
- **THEN** after 24 hours RefundSold stops and an admin is told, with the listing's id and its Order's id

## REMOVED Requirements

### Requirement: A sold listing left unrefunded is reported
**Reason**: Each listing is refunded by its own workflow, and a run that ends with a failure or passes its 24 hours is reported to an admin ("Refund within one minute after the sale").
**Migration**: The admin is told through "Workflow Needs Admin" instead of a log line repeated every minute.
