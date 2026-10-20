## Purpose

ResaleListingUseCase.RefundSold refunds the user of every resold listing the face value minus the resale fee, within 1 minute after the other fan was charged, and tells them by email.

## ADDED Requirements

### Requirement: Refund within one minute after the sale

RefundSold SHALL run every 1 minute over the listings from ResaleListing.ListSoldUnrefunded. For a listing without a refund time, it SHALL resolve the charge of the listing's Order with Order.GetProviderChargeID, refund the listing's refund amount of that charge with Order.CreateRefund for the purpose of this listing, and record it with ResaleListing.RecordRefund. A listing whose handling fails SHALL NOT stop the others and is tried again on the next run; a retried refund is issued at most once. When ResaleListing.ListSoldUnrefunded fails, RefundSold SHALL fail with that error and refund nothing.

#### Scenario: Ticket resold
- **WHEN** another fan's Order bought a listing priced 5000 yen at 18:20
- **THEN** by 18:22 the listing's user is refunded 4500 yen on the card they paid with, and the refund is recorded

#### Scenario: Refund fails once
- **WHEN** the refund of one listing fails with Unavailable
- **THEN** the other listings are still refunded and the failed one is tried again 1 minute later

#### Scenario: Refunded but not recorded
- **WHEN** a refund was issued and recording it failed
- **THEN** the next run records the same refund and the user is not refunded twice

### Requirement: Email after the refund

For a listing that has a refund time and no sold email send time, RefundSold SHALL read the listing's user with User.Get, the Order with Order.Get and the event's concert with Concert.ListByIDs, and send with ResaleListing.SendSoldEmail, to the user's email address and in the user's preferred language (Japanese when none), a message stating:
- the concert's title, date and venue;
- that one ticket was resold through official resale;
- the price, the resale fee and the refund amount, 税込 (tax-inclusive);
- that the refund goes to the card with the Order's card brand and last four digits, and that when it appears on the statement depends on the card issuer;
- that the resold ticket is no longer valid for entry.

#### Scenario: Sold email
- **WHEN** a listing priced 5000 yen was refunded
- **THEN** its user receives one email with the concert, the price 5000 yen, the fee 500 yen and the refund 4500 yen

#### Scenario: Mail unavailable
- **WHEN** ResaleListing.SendSoldEmail fails with Unavailable
- **THEN** the email is sent on a later run and the refund is not repeated

### Requirement: A sold listing left unrefunded is reported

When a Sold listing has a sold time more than 10 minutes before the run and still has no refund time, RefundSold SHALL report it, with its id and its Order's id, as needing an admin on every run, while still trying to refund it.

#### Scenario: Charge cannot be refunded
- **WHEN** a listing sold at 18:20 keeps failing to refund
- **THEN** from 18:31 every run reports it as needing an admin and tries again
