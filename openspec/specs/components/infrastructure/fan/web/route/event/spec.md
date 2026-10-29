# components/infrastructure/fan/web/route/event Specification

## Purpose
The Event page (`/events/:id`) is the public, shareable page of one first-party Event: what a fan sees when they open a link posted by an artist or a notification, whether or not they are signed in, and where ticket sales and following start.

## Requirements

### Requirement: Anyone can open the event page

The Event page SHALL be shown to guests and signed-in fans alike, without asking anyone to sign in and without waiting for the sign-in state to be known before it starts loading the event. It SHALL load the event with ConcertService.Get and the Series' dates with ConcertService.ListBySeries.

#### Scenario: Guest opens a shared link

- **WHEN** a guest who has never used the app opens `/events/<id>` of a published public event
- **THEN** the Event page shows the event and no sign-in is requested

### Requirement: What the event page shows

For an event with an event page, the Event page SHALL show:
- the Series' cover image, or a brand placeholder when there is none;
- the Series' title;
- each performing Artist's name with a follow control;
- the date with weekday, the doors-open and start times when announced, each written as "OPEN" and "START";
- the venue name and its prefecture as a localized name (never the raw code), with a link that opens the venue in Google Maps;
- the Series' description, when present;
- a share control and an add-to-calendar control;
- a ticket section.

Text the Organizer entered (title, description, venue as listed) SHALL be shown as entered in every display language; labels, dates and times SHALL follow the app's display language. The page SHALL NOT show the ticket journey status control.

#### Scenario: Event without a cover image

- **WHEN** the Series has no cover image
- **THEN** the page shows the brand placeholder in its place

#### Scenario: Start time not announced

- **WHEN** the event has a doors-open time of 18:30 and no start time
- **THEN** the page shows "OPEN 18:30" and no START time

#### Scenario: English display language

- **WHEN** the display language is English and the Organizer wrote the title in Japanese
- **THEN** the title is shown in Japanese and the date and labels in English

### Requirement: Following from the event page

The follow control of each performer SHALL follow or unfollow that Artist the same way the app's other follow controls do, for guests and signed-in fans alike, and SHALL show whether the fan already follows the Artist. A guest's follows SHALL be kept and carried into the account when the guest signs up.

#### Scenario: Guest follows the artist

- **WHEN** a guest taps the follow control of a performer on the Event page
- **THEN** the control shows the Artist as followed, and the follow is carried into the guest's account when they sign up

### Requirement: Date tabs for a series with several dates

When the Series has 2 to 4 Events, the Event page SHALL show one tab per Event, labelled with its date and weekday, in date order, with the displayed Event's tab selected. When the Series has more than 4 Events, the page SHALL instead list the other Events under the main content. Each tab and list entry SHALL be a link to that Event's own `/events/:id`, so each date can be shared and the back control returns to the previous date. A Series with one Event SHALL show neither.

#### Scenario: Two-day run

- **WHEN** the fan opens the first day of a Series with Events on 2026-11-20 and 2026-11-21
- **THEN** the page shows two tabs, the 11/20 tab selected, and tapping the 11/21 tab opens `/events/<id of the 11/21 Event>`

#### Scenario: Six-stop tour

- **WHEN** the Series has 6 Events
- **THEN** the page shows no tabs and lists the other 5 Events

### Requirement: Ticket section shows the fan's purchased tickets

The ticket section SHALL show, for a signed-in fan holding at least one Issued Ticket for the displayed Event, how many tickets they hold for it and a link to the Tickets screen. What the ticket section offers for sale is defined by the ticket sale and is not part of this page's own behavior. A guest, or a fan holding no Issued Ticket for the Event, SHALL see no purchased-tickets line.

#### Scenario: Fan holding two tickets

- **WHEN** a signed-in fan holding 2 Issued Tickets for the Event opens the page
- **THEN** the ticket section says 2 tickets are purchased and links to the Tickets screen

#### Scenario: Voided tickets are not counted

- **WHEN** a signed-in fan's only Ticket for the Event is Voided
- **THEN** no purchased-tickets line is shown

### Requirement: Sign-up started on the event page returns to it

When a guest starts sign-up from the Event page, after the sign-up completes the app SHALL show the same Event page, mark onboarding complete, and carry the guest's follows into the new account. The app SHALL NOT take the fan to the Dashboard first.

#### Scenario: Guest signs up to buy

- **WHEN** a guest who followed the performer starts sign-up on `/events/<id>` and completes it
- **THEN** the app shows `/events/<id>` signed in, the performer is followed on the account, and onboarding is complete

### Requirement: Cancelled event

When the Event is CANCELLED, the Event page SHALL show a banner stating that the concert is 中止 (cancelled), that tickets are no longer sold and that purchased tickets are refunded, together with a link to the performing Artist's other concerts; it SHALL show no sale in the ticket section. The other dates of the same Series SHALL keep their own state: a PUBLISHED date shows no banner.

#### Scenario: Shared link after cancellation

- **WHEN** a fan opens the link of an event that was cancelled, on its own or with its whole Series
- **THEN** the page shows the event with the 中止 banner, the refund notice and the link to the artist's other concerts, and nothing is offered for sale

#### Scenario: Other date of a partly cancelled tour

- **WHEN** a fan opens the link of a PUBLISHED event whose Series has another, CANCELLED event
- **THEN** the page shows no 中止 banner, and the cancelled date is marked 中止 among the dates

### Requirement: Ended event

When the Event's local date is before today's date in Japan time, the Event page SHALL show that the event has ended and SHALL show no ticket section.

#### Scenario: Day after the show

- **WHEN** a fan opens the page on 2026-11-21 for an Event dated 2026-11-20
- **THEN** the page says the event has ended and shows no ticket section

### Requirement: Event without a page

When ConcertService.Get fails with NotFound, the Event page SHALL show one "event not found" view with a link to the Dashboard, the same for every reason. When the event cannot be loaded for any other reason, the page SHALL show a retry control instead.

#### Scenario: Unlisted event

- **WHEN** a fan opens `/events/<id>` of an event whose Series is UNLISTED
- **THEN** the page shows the "event not found" view, identical to an unknown id

#### Scenario: Network failure

- **WHEN** loading the event fails with Unavailable
- **THEN** the page shows a retry control, and retrying loads the event

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

### Requirement: Sharing and adding to a calendar are reported

When the fan uses the share control or the add-to-calendar control of the Event page, the page SHALL send one usage analytics event naming the control, with the Event; for share, it SHALL also state whether the share completed or was cancelled where the device reports it.

#### Scenario: Share
- **WHEN** a fan shares the Event page and completes the share
- **THEN** one share event is sent with the Event and the share completed

### Requirement: Ticket section shows the sale and its seat types

The ticket section SHALL read the Event's sales with TicketSaleService.ListByEvent and show one of them: the sale whose window is open, otherwise the next to open, otherwise the last that ended. Sales of one event never overlap, so at most one is open. The section SHALL show the sale's name, that one account may hold up to the Event's per-account limit across all sales, with that limit, and each TicketStock of the Event with its seat type's name and price 税込 (tax-inclusive).

For a FirstCome sale:
- before its start time: the sale's start date and time in Japan time;
- within its window, for each TicketStock by its state: Available: an action to buy, adding 残りわずか (few left) when it is LowStock, and never a count; AllHeld: 売り切れ (sold out), with the note that other fans are checking out and that tickets may be available again in a few minutes; SoldOut: 売り切れ;
- after its end time: that the sale has ended.

For a Lottery sale, the section SHALL show its start and end date and time in Japan time and, while its window is open, an action to enter for each TicketStock, which opens the lottery entry screen for that sale and TicketStock; outside the window it shows no action.

For each TicketStock whose resale is open, whichever sale is shown, the section SHALL add 公式リセール (official resale) under that seat type, saying that fans who cannot attend can list their tickets from the tickets screen. It SHALL never show how many tickets are listed.

When the signed-in fan already holds or has applied for tickets of a seat type for the Event, the section SHALL offer actions only for that seat type and SHALL say that one account holds tickets of one seat type per date, naming it. When the Event has no sale, the section SHALL show no sale.

The action to buy or to enter SHALL open the checkout or the entry screen for a signed-in fan. For a guest, it SHALL start sign-up and return to the Event page. The fan's purchased tickets are shown as before.

#### Scenario: On sale with few left

- **WHEN** a guest opens the page of an open first-come sale whose S席, priced 3000 yen, is Available and LowStock
- **THEN** the section shows S席 3,000円（税込）, 残りわずか and the action to buy, with no count

#### Scenario: Two seat types

- **WHEN** an open first-come sale's event has S席 Available and A席 SoldOut
- **THEN** the section shows S席 with the action to buy and A席 as 売り切れ

#### Scenario: Guest buys

- **WHEN** a guest taps the action to buy
- **THEN** sign-up starts and, once it completes, the guest is back on the Event page

#### Scenario: Not yet on sale

- **WHEN** the first-come sale opens on 2026-11-01 10:00
- **THEN** the section shows the opening date and time, each seat type with its price, and no action to buy

#### Scenario: Temporarily all held

- **WHEN** the open first-come sale's S席 is AllHeld
- **THEN** the section shows S席 as 売り切れ with the note that tickets may be available again in a few minutes

#### Scenario: Sold out with resale open

- **WHEN** S席, priced 5000 yen, is SoldOut and its resale is open
- **THEN** the section shows S席 as 売り切れ and 公式リセール with the note that tickets can be listed from the tickets screen, and no action to buy

#### Scenario: Fan already holds another seat type

- **WHEN** a signed-in fan holds 2 S席 tickets for the event and opens the page of an open sale with S席 and A席 Available
- **THEN** the section offers the action to buy for S席 only and says the fan's tickets for this date are S席

#### Scenario: Presale over, general sale upcoming

- **WHEN** a lottery presale ended on 10 November and a first-come general sale opens on 20 November, and the fan opens the page on 15 November
- **THEN** the section shows the general sale's name and its opening date and time

#### Scenario: Lottery open

- **WHEN** a lottery sale named ファンクラブ先行 is open, with S席 priced 8000 yen
- **THEN** the section shows ファンクラブ先行, its window, S席 8,000円（税込） and the action to enter, which opens the entry screen for that sale and S席

#### Scenario: Every sale ended

- **WHEN** the presale and the general sale have both ended
- **THEN** the section shows the general sale as ended

#### Scenario: No sale

- **WHEN** no sale names the Event
- **THEN** the section shows no sale
