# Spec Delta

## MODIFIED Requirements

### Requirement: Anyone can open the concert page

The Concert page SHALL be shown to guests and signed-in fans alike, without asking anyone to sign in and without waiting for the sign-in state to be known before it starts loading the event. It SHALL load the event with ConcertService.Get and the Series' dates with ConcertService.ListBySeries.

#### Scenario: Guest opens a shared link

- **WHEN** a guest who has never used the app opens `/concerts/<id>` of a published public event
- **THEN** the Concert page shows the event and no sign-in is requested

### Requirement: Date tabs for a series with several dates

When the Series has 2 to 4 Events, the Concert page SHALL show one tab per Event, labelled with its date and weekday, in date order, with the displayed Event's tab selected. When the Series has more than 4 Events, the page SHALL instead list the other Events under the main content. Each tab and list entry SHALL be a link to that Event's own `/concerts/:id`, so each date can be shared and the back control returns to the previous date. A Series with one Event SHALL show neither.

#### Scenario: Two-day run

- **WHEN** the fan opens the first day of a Series with Events on 2026-11-20 and 2026-11-21
- **THEN** the page shows two tabs, the 11/20 tab selected, and tapping the 11/21 tab opens `/concerts/<id of the 11/21 Event>`

#### Scenario: Six-stop tour

- **WHEN** the Series has 6 Events
- **THEN** the page shows no tabs and lists the other 5 Events

### Requirement: Sign-up started on the concert page returns to it

When a guest starts sign-up from the Concert page, after the sign-up completes the app SHALL show the same Concert page, mark onboarding complete, and carry the guest's follows into the new account. The app SHALL NOT take the fan to the Timetable first.

#### Scenario: Guest signs up to buy

- **WHEN** a guest who followed the performer starts sign-up on `/concerts/<id>` and completes it
- **THEN** the app shows `/concerts/<id>` signed in, the performer is followed on the account, and onboarding is complete

### Requirement: Event without a page

When ConcertService.Get fails with NotFound, the Concert page SHALL show one "event not found" view with a link to the Timetable, the same for every reason. When the event cannot be loaded for any other reason, the page SHALL show a retry control instead.

#### Scenario: Unlisted event

- **WHEN** a fan opens `/concerts/<id>` of an event whose Series is UNLISTED
- **THEN** the page shows the "event not found" view, identical to an unknown id

#### Scenario: Network failure

- **WHEN** loading the event fails with Unavailable
- **THEN** the page shows a retry control, and retrying loads the event

### Requirement: A referral link's code is kept on the device

When the Concert page is opened with a `ref` query parameter whose value, lowercased, is a valid ReferralCode (1 to 32 lowercase ASCII letters, digits or hyphens) and the event loads, the page SHALL keep that lowercased code on the device together with the event's Series and an expiry 7 days after the page was opened, replacing any code kept before (the last link wins). This SHALL happen for guests and signed-in fans alike and SHALL NOT change what the page shows. A `ref` value that is not a valid ReferralCode, a page opened without `ref`, and a page whose event does not load SHALL leave the kept code as it is.

A kept code SHALL stay on the device across sign-up and sign-in, across other tabs and windows of the same browser, and across sign-out, until it expires or a newer valid link replaces it; after its expiry it SHALL be treated as absent. The page SHALL NOT add the code to the sign-up return path, to the links to the checkout and the lottery entry screen, to its share control or to its link preview: the checkout and the entry screen read the kept code from the device.

#### Scenario: Guest opens a referral link
- **WHEN** a guest opens `/concerts/<id>?ref=member-a` of an event of the Series XX Tour 2026 on 1 November at 12:00
- **THEN** the page shows the event as usual, and the device keeps `member-a` for XX Tour 2026 until 8 November 12:00

#### Scenario: Newer link replaces the code
- **WHEN** the device keeps `member-a` and the fan opens `/concerts/<id>?ref=member-b` of any event
- **THEN** the device keeps `member-b` for that event's Series with a new 7-day expiry

#### Scenario: Uppercase code
- **WHEN** a guest opens `/concerts/<id>?ref=Member-A`
- **THEN** the device keeps `member-a`

#### Scenario: Malformed code ignored
- **WHEN** the device keeps `member-a` and the fan opens `/concerts/<id>?ref=member_b`
- **THEN** the device still keeps `member-a`

#### Scenario: Code survives sign-up
- **WHEN** a guest opens `/concerts/<id>?ref=member-a`, starts sign-up from the page and completes it
- **THEN** the app shows `/concerts/<id>` without the query, and the device still keeps `member-a`

#### Scenario: Unknown event
- **WHEN** a fan opens `/concerts/<id>?ref=member-a` of an event that is not found
- **THEN** no code is kept
