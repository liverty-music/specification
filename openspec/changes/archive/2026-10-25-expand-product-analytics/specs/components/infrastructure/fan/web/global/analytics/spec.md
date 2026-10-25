## ADDED Requirements

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
