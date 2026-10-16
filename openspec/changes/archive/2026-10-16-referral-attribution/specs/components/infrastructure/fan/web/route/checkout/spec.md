## ADDED Requirements

### Requirement: The kept referral code goes with the checkout

When continuing holds the tickets with CheckoutService.Start, the checkout SHALL send the referral code kept on the device by the Event page when the code has not expired and was kept for the Series of the checkout's event, and SHALL send no code otherwise. Sending a code SHALL NOT change anything the fan sees. Placing the order, failing or leaving the checkout SHALL leave the kept code on the device.

#### Scenario: Purchase three days after the link
- **WHEN** a fan who opened a link with `ref=member-a` for an event of XX Tour 2026 three days ago continues the checkout of any event of XX Tour 2026
- **THEN** Start is called with the code `member-a`

#### Scenario: Code expired
- **WHEN** the fan opened that link 8 days ago
- **THEN** Start is called without a code

#### Scenario: Another Series
- **WHEN** the kept code was kept for XX Tour 2026 and the fan checks out an event of another Series
- **THEN** Start is called without a code

#### Scenario: Direct visit
- **WHEN** no code is kept on the device
- **THEN** Start is called without a code
