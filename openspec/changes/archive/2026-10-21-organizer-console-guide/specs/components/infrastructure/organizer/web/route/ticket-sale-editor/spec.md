## MODIFIED Requirements

### Requirement: Prerequisites explained

When the event is not published, has no start time, or the Organizer does not have complete business details, the screen SHALL say which is missing and not offer to save. For missing business details, it SHALL say they are entered by Liverty Music during vetting. Each of these notices SHALL also link to the members' guide, opened in a new tab, at the chapter that explains it: 公演をつくって公開する for an unpublished event or a missing start time, and 事業者情報と受取口座 for incomplete business details.

#### Scenario: No start time

- **WHEN** the member opens the editor for an event without a start time
- **THEN** the screen says to set the start time in the concert editor first and links to it and to the guide's chapter 公演をつくって公開する

#### Scenario: Business details incomplete

- **WHEN** the member opens the editor for a published, timed event of an Organizer without a business phone number
- **THEN** the screen says the business details are entered by Liverty Music during vetting, links to the guide's chapter 事業者情報と受取口座, and saving is not offered
