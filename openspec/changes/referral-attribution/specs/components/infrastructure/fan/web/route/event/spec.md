## ADDED Requirements

### Requirement: A referral link's code is kept on the device

When the Event page is opened with a `ref` query parameter whose value, lowercased, is a valid ReferralCode (1 to 32 lowercase ASCII letters, digits or hyphens) and the event loads, the page SHALL keep that lowercased code on the device together with the event's Series and an expiry 7 days after the page was opened, replacing any code kept before (the last link wins). This SHALL happen for guests and signed-in fans alike and SHALL NOT change what the page shows. A `ref` value that is not a valid ReferralCode, a page opened without `ref`, and a page whose event does not load SHALL leave the kept code as it is.

A kept code SHALL stay on the device across sign-up and sign-in, across other tabs and windows of the same browser, and across sign-out, until it expires or a newer valid link replaces it; after its expiry it SHALL be treated as absent. The page SHALL NOT add the code to the sign-up return path, to the links to the checkout and the lottery entry screen, to its share control or to its link preview: the checkout and the entry screen read the kept code from the device.

#### Scenario: Guest opens a referral link
- **WHEN** a guest opens `/events/<id>?ref=member-a` of an event of the Series XX Tour 2026 on 1 November at 12:00
- **THEN** the page shows the event as usual, and the device keeps `member-a` for XX Tour 2026 until 8 November 12:00

#### Scenario: Newer link replaces the code
- **WHEN** the device keeps `member-a` and the fan opens `/events/<id>?ref=member-b` of any event
- **THEN** the device keeps `member-b` for that event's Series with a new 7-day expiry

#### Scenario: Uppercase code
- **WHEN** a guest opens `/events/<id>?ref=Member-A`
- **THEN** the device keeps `member-a`

#### Scenario: Malformed code ignored
- **WHEN** the device keeps `member-a` and the fan opens `/events/<id>?ref=member_b`
- **THEN** the device still keeps `member-a`

#### Scenario: Code survives sign-up
- **WHEN** a guest opens `/events/<id>?ref=member-a`, starts sign-up from the page and completes it
- **THEN** the app shows `/events/<id>` without the query, and the device still keeps `member-a`

#### Scenario: Unknown event
- **WHEN** a fan opens `/events/<id>?ref=member-a` of an event that is not found
- **THEN** no code is kept
