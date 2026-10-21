# components/usecase/notification/send-resale-sold Specification

## Purpose
NotificationUseCase.SendResaleSold tells a fan that a ticket they listed for official resale (公式リセール) was bought by another fan and how much they are refunded, once the refund is made.

## Requirements

### Requirement: Sold email after every refunded listing

SendResaleSold SHALL run for each ResaleListing announced as refunded, with its user, its Order and its event. It SHALL read:
- the listing with ResaleListing.Get;
- the listing's user with User.Get;
- the Order with Order.Get;
- the event's concert with Concert.ListByIDs.

It SHALL send, with ResaleListing.SendSoldEmail to the user's email address and in the user's preferred language (Japanese when none), a message stating:
- the concert's title, date and venue;
- that one ticket was resold through official resale;
- the price, the resale fee and the refund amount, 税込 (tax-inclusive);
- that the refund goes to the card with the Order's card brand and last four digits, and that when it appears on the statement depends on the card issuer;
- that the resold ticket is no longer valid for entry.

When reading or sending fails, SendResaleSold SHALL fail with that error and is run again; ResaleListing.SendSoldEmail keeps it to one email per listing.

#### Scenario: Sold email
- **WHEN** a listing priced 5000 yen is announced as refunded
- **THEN** its user receives one email with the concert, the price 5000 yen, the fee 500 yen and the refund 4500 yen

#### Scenario: Listing announced twice
- **WHEN** the same announcement is delivered twice
- **THEN** the user receives one email

#### Scenario: Mail unavailable
- **WHEN** ResaleListing.SendSoldEmail fails with Unavailable
- **THEN** SendResaleSold fails and the email is sent when it runs again
