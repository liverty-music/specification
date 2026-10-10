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

Text the organizer entered (title, description, venue as listed) SHALL be shown as entered in every display language; labels, dates and times SHALL follow the app's display language. The page SHALL NOT show the ticket journey status control.

#### Scenario: Event without a cover image

- **WHEN** the Series has no cover image
- **THEN** the page shows the brand placeholder in its place

#### Scenario: Start time not announced

- **WHEN** the event has a doors-open time of 18:30 and no start time
- **THEN** the page shows "OPEN 18:30" and no START time

#### Scenario: English display language

- **WHEN** the display language is English and the organizer wrote the title in Japanese
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

When the Series is CANCELLED, the Event page SHALL show a banner stating that the concert is 中止 (cancelled), that tickets are no longer sold and that purchased tickets are refunded, together with a link to the performing Artist's other concerts; it SHALL show no sale in the ticket section.

#### Scenario: Shared link after cancellation

- **WHEN** a fan opens the link of an event whose Series was cancelled
- **THEN** the page shows the event with the 中止 banner, the refund notice and the link to the artist's other concerts, and nothing is offered for sale

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
