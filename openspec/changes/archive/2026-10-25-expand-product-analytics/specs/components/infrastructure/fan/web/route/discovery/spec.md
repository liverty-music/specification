## ADDED Requirements

### Requirement: A guest's follows and the ready timetable are reported

While the fan is a guest, each follow that takes effect SHALL send one usage analytics event with the artist and the number of artists the guest now follows; a signed-in fan's follow is reported by the server. When the onboarding progress row is shown as the link to the Dashboard (the row is hidden while search results are shown), the page SHALL send one usage analytics event with the number of followed artists and of artists with concerts at that moment, at most once per visit to Discovery.

#### Scenario: Guest follows a fifth artist
- **WHEN** a guest who follows 4 artists follows another
- **THEN** one guest-follow event is sent with that artist and a count of 5

#### Scenario: Timetable becomes ready
- **WHEN** an onboarding fan's follows make the progress row ready
- **THEN** one timetable-ready event is sent with the two counts

#### Scenario: Ready while searching
- **WHEN** an onboarding fan's follow from search results makes the progress row ready
- **THEN** no timetable-ready event is sent until the search is closed and the row is shown
