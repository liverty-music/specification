# components/infrastructure/fan/web/global/analytics Specification

## Purpose
How the fan app's usage analytics treats the addresses of the app's own pages: analytics events never carry the query string of an app address, so a referral code or any other value in a link stays on the platform.

## Requirements

### Requirement: Analytics events carry no query string of the app's own addresses

Before any usage analytics event leaves the device, the fan app SHALL remove the query string and the fragment from every address in the event that points at the app's own origin, including the current address, the first address of the visit and the address the fan came from inside the app. Addresses of other sites SHALL be sent as they are. This SHALL apply to every event the app sends, whether or not the fan is signed in, and SHALL NOT change which events are sent or when.

An error report (`components/infrastructure/fan/web/global/error-banner`) is the one exception, and it applies to its current address only. On that address the query keys `artists`, `journey` and `from` SHALL be kept with their values, because the dashboard they configure cannot be reproduced without them. Every other key and the fragment SHALL be removed. The value of `ref` SHALL never be sent; the error report SHALL state only whether the current address had a `ref` key. The first address of the visit and the address the fan came from SHALL be stripped as for every other event.

#### Scenario: Event on a referral link
- **WHEN** a fan opens `/events/<id>?ref=member-a` with analytics on and the page sends an analytics event
- **THEN** the event's current address is `/events/<id>` on the app's origin, without `?ref=member-a`

#### Scenario: First address of the visit
- **WHEN** the fan's visit started on `/events/<id>?ref=member-a` and a later page sends an analytics event
- **THEN** no address in the event contains `ref=member-a`

#### Scenario: Another site's address
- **WHEN** a fan arrives from `https://x.com/some/post?s=20` and the page sends an analytics event
- **THEN** the address the fan came from is sent as `https://x.com/some/post?s=20`

#### Scenario: Analytics off
- **WHEN** the fan has turned analytics off in Settings
- **THEN** no analytics event is sent, as before

#### Scenario: Error report on a filtered dashboard
- **WHEN** an error is reported while the fan is on `/dashboard?artists=a1,a2&journey=tour&from=welcome&utm_source=x#top`
- **THEN** the error report's current address is `/dashboard?artists=a1,a2&journey=tour&from=welcome` on the app's origin

#### Scenario: Error report on a referral link
- **WHEN** an error is reported while the fan is on `/events/<id>?ref=member-a`
- **THEN** the error report's current address is `/events/<id>`, no address in the report contains `member-a`, and the report states that a `ref` key was present

#### Scenario: Other events keep the dashboard filter out
- **WHEN** the fan is on `/dashboard?artists=a1` and the page sends an analytics event that is not an error report
- **THEN** the event's current address is `/dashboard`, without `?artists=a1`

### Requirement: Every screen change and every leave is recorded

With analytics on, the fan app SHALL send one page view each time the fan arrives on a screen, including the first screen of a visit and every in-app navigation, and one page leave when the fan leaves the app or closes the tab. Both SHALL follow the query-string rule of this surface. A navigation that stays on the same screen and only changes its query string SHALL NOT send a page view.

#### Scenario: In-app navigation
- **WHEN** a fan with analytics on moves from Welcome to Discovery and then to the Dashboard
- **THEN** three page views are sent, one per screen, in that order

#### Scenario: Leaving the app
- **WHEN** the fan closes the tab on the Dashboard
- **THEN** one page leave is sent for the Dashboard

#### Scenario: No page views with analytics off
- **WHEN** the fan has turned analytics off in Settings
- **THEN** no page view and no page leave is sent

### Requirement: Campaign values travel as their own properties

When the address a fan arrived on carries any of the campaign keys `utm_source`, `utm_medium`, `utm_campaign`, `utm_content` and `utm_term`, every analytics event of that visit SHALL carry each present key and its value as its own property, and the fan's first such values SHALL be kept as the fan's first campaign. Addresses in the event still follow the query-string rule of this surface, and a referral code (`ref`) SHALL never be sent as a property.

#### Scenario: Campaign link with a referral code
- **WHEN** a fan opens `/welcome?utm_source=x&utm_campaign=launch&ref=member-a`
- **THEN** each event of the visit carries `utm_source` = `x` and `utm_campaign` = `launch`, its current address is `/welcome`, and no address or property contains `member-a`

#### Scenario: No campaign keys
- **WHEN** a fan opens `/discovery` with no query string
- **THEN** the events carry no campaign property

### Requirement: Session recordings hide what the fan types and reads

When both Analytics and Session replay are on in Settings, the fan app SHALL record the session for replay with every text on screen and every input value masked, including password and hidden fields, and SHALL NOT record the checkout, lottery entry, identity check and Settings screens at all. With either toggle off, nothing SHALL be recorded. A recording SHALL be linked to the same person as the fan's analytics events.

#### Scenario: Masked text
- **WHEN** a recorded fan opens the Dashboard, where artist names and the fan's home area are shown
- **THEN** the recording shows the layout and the fan's taps, and every text in it is masked

#### Scenario: Screen that is never recorded
- **WHEN** a recorded fan opens the checkout
- **THEN** no recording is made while the checkout is shown, and recording resumes on the next screen that is recorded

#### Scenario: Session replay off
- **WHEN** the fan turns Session replay off and keeps Analytics on
- **THEN** recording stops and events are still sent

### Requirement: Events state how the app is running

Every analytics event sent from a page of the fan app SHALL state whether the fan app runs installed on the device (standalone) or in a browser tab, including after the fan turns analytics off and on again or signs out. Events the service worker sends, which run outside any page, do not state it.

#### Scenario: Installed app
- **WHEN** a fan opens the app from the home-screen icon and an event is sent
- **THEN** the event states that the app runs installed

#### Scenario: Analytics turned off and on again
- **WHEN** a fan in a browser tab turns analytics off and then on again in Settings, and an event is sent
- **THEN** the event states that the app runs in a browser tab
