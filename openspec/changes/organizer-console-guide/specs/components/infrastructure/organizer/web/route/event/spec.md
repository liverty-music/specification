## MODIFIED Requirements

### Requirement: The Sales tab explains a missing prerequisite

The Sales tab SHALL say why no sale can be started, and link to where to fix it, when the event is not published (link: the event's 公開する action), has no start time (link: the concert editor), or the Organizer's business details (legal name, representative name, business address, business phone number, contact email) are not complete (no link to a fix; it says they are entered by Liverty Music during vetting and how to contact Liverty Music). Each of these notices SHALL also link to the members' guide, opened in a new tab, at the chapter that explains it: 公演をつくって公開する for an unpublished event or a missing start time, and 事業者情報と受取口座 for incomplete business details. While a prerequisite is missing, the tab SHALL not offer to start a sale.

#### Scenario: Draft event

- **WHEN** a member opens the Sales tab of a draft event
- **THEN** it says 販売を始めるには、公演を公開してください with a link to publish and a link to the guide's chapter 公演をつくって公開する, and no sale can be started

#### Scenario: No start time

- **WHEN** the event is published and has no start time
- **THEN** the tab says the start time must be set first and links to the concert editor and to the guide's chapter 公演をつくって公開する

#### Scenario: Business details incomplete

- **WHEN** the event is published and timed and the Organizer has no business address
- **THEN** the tab says the business details are entered by Liverty Music during vetting, links to the guide's chapter 事業者情報と受取口座, and no sale can be started

### Requirement: The Reception tab explains a missing prerequisite

The Reception tab SHALL say, and not offer to issue a Scanner, when the event is not published (link: the event's 公開する action) or has no start time (link: the concert editor). Each of these notices SHALL also link to the members' guide, opened in a new tab, at the chapter 公演をつくって公開する.

#### Scenario: Unpublished event

- **WHEN** the member opens the Reception tab of a draft event
- **THEN** the tab says the event must be published before links can be issued, with a link to the guide's chapter 公演をつくって公開する

#### Scenario: Event without a start time

- **WHEN** the member opens the Reception tab of a published event without a start time
- **THEN** the tab says the event needs a start time before links can be issued, with a link to the guide's chapter 公演をつくって公開する
