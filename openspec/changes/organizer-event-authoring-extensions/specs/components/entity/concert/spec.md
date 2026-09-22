## ADDED Requirements

### Requirement: Rich media on a concert page

The system SHALL let an organizer attach multiple images (a gallery beyond
the single MVP cover), a video embed (e.g. YouTube), and external links
(official site / SNS) to a concert.

#### Scenario: Multiple images and a video embed

- **WHEN** an organizer adds several images and a video URL to a draft
- **THEN** the published concert page SHALL show the image gallery and the
  embedded video

### Requirement: Streaming and hybrid concerts

The system SHALL let an organizer mark a concert's mode as `venue`,
`online`, or `hybrid`, and for online/hybrid capture a stream method/URL.
For an `online` concert the venue SHALL be optional.

#### Scenario: Online concert without a physical venue

- **WHEN** an organizer authors an `online` concert with a stream URL and no
  venue
- **THEN** the system SHALL accept and publish it without requiring a venue

### Requirement: Discovery metadata

The system SHALL let an organizer set a category/genre and search keywords
on a concert to improve its discoverability.

#### Scenario: Category and keywords improve search

- **WHEN** a concert is published with a category and keywords
- **THEN** the system SHALL use them in search/discovery ranking

### Requirement: Japan-idiomatic structured fields

The system SHALL let an organizer set structured 注意事項 (notices/terms),
問い合わせ先 (contact — built-in form or email/phone/URL), and 年齢制限 (age
restriction) on a concert, shown on the page and in the confirmation path.

#### Scenario: Notices, contact, and age restriction render

- **WHEN** a concert with notices, a contact, and an age restriction is
  published
- **THEN** the page SHALL display each in its own structured section

### Requirement: Password-protected visibility

In addition to `PUBLIC` and `UNLISTED`, the system SHALL support a
`PASSWORD` visibility where a viewer must enter the correct password to see
the concert page.

#### Scenario: Password gate on a protected concert

- **WHEN** a viewer opens a `PASSWORD` concert URL
- **THEN** the system SHALL require the correct password before serving the
  page
