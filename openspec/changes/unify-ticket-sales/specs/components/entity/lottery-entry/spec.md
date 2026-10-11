# Spec Delta

## Purpose

A LotteryEntry is one fan account's entry into the lottery for one TicketType: a request for a companion group of tickets allocated all-or-nothing, and the reference to the authorization (hold) placed on the fan's card for the amount until the draw. A fan builds the entry as a Draft, authorizes the hold on it, and confirms it; only a confirmed (Entered) entry takes part in the draw. The fan's 本人確認 (identity check) details are the User's full name and phone number.

| attribute | meaning | constraint |
|-----------|---------|------------|
| id | the entry's identity | required, assigned on creation |
| ticket type | the TicketType entered | required; its sale's method is Lottery |
| user | the fan account that entered | required |
| requested ticket count | size of the companion group, allocated all-or-nothing | required, 1 to the ticket type's per-account limit |
| authorization | reference to the hold placed on the fan's card | absent on a Draft until the hold is opened; required from Entered on; 1-255 characters, opaque |
| state | lifecycle | Draft, Entered, Won, Lost or Withdrawn |
| draw position | the entry's position in its ticket type's random draw order | absent before the draw; set only by the draw |

```mermaid
erDiagram
  TicketType ||--o{ LotteryEntry : "receives"
  User ||--o{ LotteryEntry : "enters"
  LotteryEntry ||--o| Order : "is purchased by"
```

```mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> Entered
  Draft --> Withdrawn
  Entered --> Won
  Entered --> Lost
  Entered --> Withdrawn
  Won --> [*]
  Lost --> [*]
  Withdrawn --> [*]
```

## ADDED Requirements

### Requirement: A new entry starts as a Draft

A LotteryEntry SHALL start in state Draft, with no authorization and no draw position.

#### Scenario: New entry
- **WHEN** a LotteryEntry is created
- **THEN** its state is Draft and it has no authorization and no draw position

### Requirement: Confirmable only as an authorized Draft

An entry SHALL be confirmable, that is able to become Entered, only while its state is Draft and it has an authorization.

#### Scenario: Authorized draft
- **WHEN** the entry is a Draft with an authorization
- **THEN** it is confirmable

#### Scenario: Draft without a hold
- **WHEN** the entry is a Draft with no authorization
- **THEN** it is not confirmable

#### Scenario: Already entered
- **WHEN** the entry is Entered, Won, Lost or Withdrawn
- **THEN** it is not confirmable

### Requirement: Requested ticket count fits the ticket type

The requested ticket count SHALL be at least 1 and at most the ticket type's per-account limit.

#### Scenario: Count within the limit
- **WHEN** the ticket type allows 4 tickets per account and 2 are requested
- **THEN** the count is valid

#### Scenario: Zero tickets requested
- **WHEN** 0 tickets are requested
- **THEN** the count is invalid

#### Scenario: Count over the limit
- **WHEN** the ticket type allows 4 tickets per account and 5 are requested
- **THEN** the count is invalid

### Requirement: Active entries

An entry SHALL be active unless its state is Withdrawn; Draft, Won and Lost entries stay active.

#### Scenario: Withdrawn entry is not active
- **WHEN** the state is Withdrawn
- **THEN** the entry is not active

#### Scenario: Draft or drawn entry is active
- **WHEN** the state is Draft, Won or Lost
- **THEN** the entry is active

### Requirement: Withdrawable only before the draw

An entry SHALL be withdrawable only while its state is Draft or Entered, that is before the draw has run for it.

#### Scenario: Draft or entered entry
- **WHEN** the state is Draft or Entered
- **THEN** the entry is withdrawable

#### Scenario: Drawn or withdrawn entry
- **WHEN** the state is Won, Lost or Withdrawn
- **THEN** the entry is not withdrawable

### Requirement: Accepted card brands

A card SHALL be accepted for an entry unless its brand is American Express; a card whose brand is unknown is accepted.

#### Scenario: American Express
- **WHEN** the card brand is American Express
- **THEN** the card is not accepted

#### Scenario: Other or unknown brand
- **WHEN** the card brand is Visa, Mastercard, JCB, Diners, Discover or unknown
- **THEN** the card is accepted
