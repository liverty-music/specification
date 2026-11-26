## MODIFIED Requirements

### Requirement: Only a signed-in fan can open the center

Only a signed-in fan SHALL see the center: a guest who opens `/notifications` SHALL be shown a notice and sent to `/welcome`, and the center SHALL NOT be shown. Where the guest then arrives is decided by the Welcome page: a returning guest, as its "Returning Guest Redirect" requirement defines one, goes on to the Timetable with the notice, and any other guest sees the Welcome page.

#### Scenario: Guest
- **WHEN** a guest opens `/notifications`
- **THEN** a notice is shown, the guest is sent to `/welcome`, and the center is not shown
