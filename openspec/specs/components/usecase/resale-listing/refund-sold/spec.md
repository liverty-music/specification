# components/usecase/resale-listing/refund-sold Specification

## Purpose
ResaleListingUseCase.RefundSold refunds the user of every resold listing the face value minus the resale fee, within 1 minute after the other fan was charged, and announces the refund so the user is told by email.

## Requirements

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

### Requirement: Refund announced

For each listing it refunds, and for each listing from ResaleListing.ListSoldUnrefunded that has a refund time and no sold email send time, RefundSold SHALL announce that the listing was refunded, carrying the listing, its user, its Order and its event. Each announcement is a new message; consumers SHALL treat a repeated announcement of a listing as one. A failed announcement SHALL NOT stop the other listings and is made again on the next run; the refund is not repeated.

#### Scenario: Refund announced
- **WHEN** a listing is refunded
- **THEN** the refund is announced once with the listing, its user, its Order and its event

#### Scenario: Announcement fails
- **WHEN** announcing a refunded listing fails
- **THEN** the next run announces it again and does not refund it again

#### Scenario: Email already sent
- **WHEN** a refunded listing has a sold email send time
- **THEN** it is not announced again

### Requirement: A sold listing left unrefunded is reported

When a Sold listing has a sold time more than 10 minutes before the run and still has no refund time, RefundSold SHALL report it, with its id and its Order's id, as needing an admin on every run, while still trying to refund it.

#### Scenario: Charge cannot be refunded
- **WHEN** a listing sold at 18:20 keeps failing to refund
- **THEN** from 18:31 every run reports it as needing an admin and tries again
