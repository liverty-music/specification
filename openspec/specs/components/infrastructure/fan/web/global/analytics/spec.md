# components/infrastructure/fan/web/global/analytics Specification

## Purpose
How the fan app's usage analytics treats the addresses of the app's own pages: analytics events never carry the query string of an app address, so a referral code or any other value in a link stays on the platform.

## Requirements

### Requirement: Analytics events carry no query string of the app's own addresses

Before any usage analytics event leaves the device, the fan app SHALL remove the query string and the fragment from every address in the event that points at the app's own origin, including the current address, the first address of the visit and the address the fan came from inside the app. Addresses of other sites SHALL be sent as they are. This SHALL apply to every event the app sends, whether or not the fan is signed in, and SHALL NOT change which events are sent or when.

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
