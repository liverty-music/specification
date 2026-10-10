# Spec Delta

## MODIFIED Requirements

### Requirement: A lottery window lasts 1 to 14 days

A TicketSale's end time, when it has one, SHALL be after its start time. When an Organizer's sale has the method Lottery, its window SHALL last at least 1 day and at most 14 days. A discovered sale's window SHALL have no limit on its length.

#### Scenario: Lottery window within bounds
- **WHEN** an Organizer's Lottery sale runs for 10 days
- **THEN** the window is valid

#### Scenario: Lottery window shorter than 1 day
- **WHEN** an Organizer's Lottery sale runs for 23 hours
- **THEN** the window is invalid

#### Scenario: Lottery window longer than 14 days
- **WHEN** an Organizer's Lottery sale runs for 14 days and 1 hour
- **THEN** the window is invalid

#### Scenario: End not after start
- **WHEN** the end time equals or precedes the start time
- **THEN** the window is invalid

#### Scenario: Discovered lottery longer than 14 days
- **WHEN** a discovered Lottery sale runs from 1 October to 31 October
- **THEN** the window is valid

### Requirement: A sale has a name

An Organizer's sale SHALL have a name of 1 to 100 characters. A discovered sale SHALL have no name.

#### Scenario: Named sale
- **WHEN** an Organizer's sale is named ファンクラブ先行
- **THEN** the name is valid

#### Scenario: Empty name
- **WHEN** an Organizer's sale has an empty name
- **THEN** the sale is invalid

#### Scenario: Discovered sale without a name
- **WHEN** a discovered sale has no name
- **THEN** the sale is valid

## ADDED Requirements

### Requirement: An Organizer's sale or a discovered sale

A TicketSale of a Series that has an Organizer SHALL be that Organizer's sale. It SHALL offer at least one TicketType and SHALL have no discovered time. A TicketSale of a Series without an Organizer SHALL be a discovered sale. It SHALL offer no TicketType, SHALL have a discovered time, SHALL have the verification requirement None, and SHALL never be drawn.

#### Scenario: Organizer's presale
- **WHEN** a sale belongs to a Series owned by an Organizer and offers TicketTypes for two of its events
- **THEN** it is the Organizer's sale

#### Scenario: Sale found by discovery
- **WHEN** a sale belongs to a Series that has no Organizer
- **THEN** it is a discovered sale and offers no TicketType

#### Scenario: Discovered sale with a TicketType
- **WHEN** a sale of a Series without an Organizer offers a TicketType
- **THEN** the sale is invalid

#### Scenario: Organizer's sale without a TicketType
- **WHEN** a sale of a Series with an Organizer offers no TicketType
- **THEN** the sale is invalid

### Requirement: Required times depend on the method and the kind of sale

Every TicketSale SHALL have a start time. A Lottery sale SHALL have an end time. An Organizer's sale SHALL have an end time. A discovered FirstCome sale's end time SHALL be optional, and an absent end time SHALL mean the sale ends when tickets run out. A lottery result time (当落発表, the announced result time) SHALL be optional. It SHALL appear only on a discovered Lottery sale and SHALL NOT be before the end time.

#### Scenario: First-come sale until sold out
- **WHEN** a discovered FirstCome sale has a start time and no end time
- **THEN** the sale is valid

#### Scenario: Lottery without a close
- **WHEN** a Lottery sale has no end time
- **THEN** the sale is invalid

#### Scenario: Organizer's first-come sale without a close
- **WHEN** an Organizer's FirstCome sale has no end time
- **THEN** the sale is invalid

#### Scenario: Result before close
- **WHEN** a discovered Lottery sale's lottery result time is before its end time
- **THEN** the sale is invalid

#### Scenario: Result on a first-come sale
- **WHEN** a discovered FirstCome sale has a lottery result time
- **THEN** the sale is invalid

#### Scenario: Result time on an Organizer's lottery
- **WHEN** an Organizer's Lottery sale has a lottery result time
- **THEN** the sale is invalid

### Requirement: Result time of a lottery

A Lottery sale's result time SHALL be its lottery result time when it has one. An Organizer's Lottery sale's result time SHALL be its end time, because its draw runs within 1 minute after the end time. A discovered Lottery sale without a lottery result time SHALL have no result time. A FirstCome sale SHALL have no result time.

#### Scenario: Discovered lottery with an announced result
- **WHEN** a discovered Lottery sale closes on 22 October 23:59 and has the lottery result time 3 November 15:00
- **THEN** its result time is 3 November 15:00

#### Scenario: Organizer's lottery
- **WHEN** an Organizer's Lottery sale ends on 22 October 23:59
- **THEN** its result time is 22 October 23:59

#### Scenario: Discovered lottery without an announced result
- **WHEN** a discovered Lottery sale has no lottery result time
- **THEN** it has no result time

### Requirement: The discovered time is set once

A discovered sale's discovered time SHALL be set when the sale is first stored and SHALL never change afterwards, however often the sale is discovered again.

#### Scenario: Re-discovery keeps the discovered time
- **WHEN** a sale first stored on 1 June is discovered again on 5 June with new details
- **THEN** its discovered time stays 1 June

### Requirement: A sale not yet over

A TicketSale SHALL be not yet over at an instant that is before its end time. A sale without an end time SHALL be not yet over only before its start time, because nothing tells when its tickets run out.

#### Scenario: Lottery before its close
- **WHEN** a Lottery sale closes on 22 October 23:59 and the instant is 20 October
- **THEN** the sale is not yet over

#### Scenario: First-come sale until sold out has opened
- **WHEN** a FirstCome sale without an end time opened at 18:30 today and the instant is 18:31
- **THEN** the sale is over
