## ADDED Requirements

### Requirement: Leaving for the source and adding to a calendar are reported

When the fan opens the concert's source link or its add-to-calendar link from the event detail sheet, the fan app SHALL send one usage analytics event naming which link, with the event and the artist.

#### Scenario: Source link
- **WHEN** the fan taps the source link of a concert in the detail sheet
- **THEN** one event is sent naming the source link, the event and the artist
