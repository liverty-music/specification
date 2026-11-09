# Spec Delta

## ADDED Requirements

### Requirement: Artists whose activity has ended are not searched

SearchNewConcerts SHALL return no concerts, and SHALL perform no external search, when the Artist's activity_ended is true. When the Artist's activity_ended becomes false again, it SHALL be searched again.

#### Scenario: Ended artist
- **WHEN** SearchNewConcerts is called for an Artist whose activity_ended is true
- **THEN** no external search is performed and no concerts are returned

#### Scenario: Ended artist in the daily run
- **WHEN** a followed Artist's activity_ended is true at the daily run
- **THEN** that Artist is not searched, and the run continues with the next Artist without counting a failure

#### Scenario: Ended artist followed for the first time
- **WHEN** a fan is the first to follow an Artist whose activity_ended is true
- **THEN** no external search is performed
