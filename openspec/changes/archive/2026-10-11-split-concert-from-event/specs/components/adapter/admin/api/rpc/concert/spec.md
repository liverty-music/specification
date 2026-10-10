## ADDED Requirements

### Requirement: Listed concerts come with their series and artists once

List SHALL return, together with the Concerts, every Series and every Artist those Concerts refer to, once each; a Concert carries only the id of its Series (through its Event) and the ids of its Artists. Every returned Series SHALL carry the same fields as on the fan concert service, and its share token SHALL never be returned.

#### Scenario: Two approved concerts of one series

- **WHEN** an admin lists the concerts and two of them belong to the same Series and share an Artist
- **THEN** the response carries that Series once and that Artist once, and both Concerts refer to them by id
