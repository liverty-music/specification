## ADDED Requirements

### Requirement: A guest's follows and the coach mark are reported

While the fan is a guest, each follow that takes effect SHALL send one usage analytics event with the artist and the number of artists the guest now follows; a signed-in fan's follow is reported by the server. When the coach mark towards the Dashboard appears, the page SHALL send one usage analytics event with the number of followed artists and of artists with concerts at that moment.

#### Scenario: Guest follows a fifth artist
- **WHEN** a guest who follows 4 artists follows another
- **THEN** one guest-follow event is sent with that artist and a count of 5

#### Scenario: Coach mark appears
- **WHEN** the progression condition is reached and the coach mark appears
- **THEN** one coach-mark-shown event is sent with the two counts
