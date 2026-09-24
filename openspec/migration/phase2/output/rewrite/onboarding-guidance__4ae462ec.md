<!-- spec: onboarding-guidance | target: components/infrastructure/fan/web/route/discovery | flags: CLASSNAME | new_name: Followed count reflects localStorage state -->

### Requirement: Followed count reflects localStorage state
The count of followed artists SHALL be an observable value that updates whenever the user follows, unfollows, or clears all followed artists, so that bindings re-evaluate immediately.

#### Scenario: Initial page load with existing guest data
- **WHEN** the user navigates to `/discover` during onboarding and localStorage's guest followed-artists entry contains 3 artists
- **THEN** the orb SHALL reflect the accumulated intensity for 3 follows
- **AND** the coach-mark activation conditions SHALL evaluate correctly

#### Scenario: Follow an artist during onboarding
- **WHEN** the user taps a bubble to follow an artist
- **THEN** the orb SHALL receive a color injection with the bubble's hue
- **AND** the orb's base intensity SHALL increase per the easing curve

#### Scenario: Unfollow an artist
- **WHEN** the user unfollows a previously followed artist
- **THEN** the followed count SHALL decrement by 1 immediately
- **AND** the orb's base intensity SHALL NOT decrease (visual intensity is one-directional within a session)
