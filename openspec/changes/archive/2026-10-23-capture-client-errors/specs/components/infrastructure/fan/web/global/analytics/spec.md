# Spec Delta

## MODIFIED Requirements

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
