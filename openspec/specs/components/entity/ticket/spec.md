# Ticket

## Purpose

A Ticket is one account-bound admission right to an event, issued from an Order. Every Ticket is a 特定興行入場券 (covered ticket): it names the event and its holder and states that resale without the organizer's consent is prohibited.

| attribute | meaning | constraint |
|-----------|---------|------------|
| id | the ticket's identity | required, assigned on issuance |
| order | the Order that issued it | required |
| holder | the account the ticket is bound to | required; never changes (official resale voids the ticket and issues a new one) |
| event | the event it admits to, which gives the date and venue on its face | required |
| holder full name | the holder's name noted on the face (本人確認) | required, 1-200 characters |
| holder phone number | the holder's contact phone noted on the face (本人確認) | required, E.164: `+` then 2-15 digits, first digit not 0 |
| verified identity | the verified identity the ticket is bound to | optional; set only when the phase required verification |
| resale without consent prohibited | the face states that resale without the organizer's consent is prohibited | always true |
| status | lifecycle; a Voided ticket is no longer valid for entry | Issued or Voided |
| issued time | when the ticket was issued | required |
| admitted time | when the ticket was let in at the venue | optional; absent until admitted, set once and kept when the ticket is later Voided |

```mermaid
erDiagram
  Order ||--|{ Ticket : "issues"
  User ||--o{ Ticket : "holds"
  Event ||--o{ Ticket : "is admitted by"
  VerifiedIdentity |o--o{ Ticket : "binds"
```

```mermaid
stateDiagram-v2
  [*] --> Issued
  Issued --> Voided
  Voided --> [*]
```

## Requirements

### Requirement: Every ticket is a covered ticket

Every Ticket SHALL carry the three conditions of a 特定興行入場券: its face states that resale without the organizer's consent is prohibited; it names the event (date and venue) and the eligible person, who is the holder named by the holder full name, with no seat assigned; and it records the holder's name and contact phone (本人確認).

#### Scenario: Issued ticket face

- **WHEN** a Ticket is issued
- **THEN** it states that resale without consent is prohibited, names its event and its holder, carries the holder's name and phone, and has no seat

#### Scenario: Resale flag cannot be false

- **WHEN** a Ticket states resale without consent is not prohibited
- **THEN** the Ticket is invalid

### Requirement: A new ticket starts Issued

A Ticket SHALL start in status Issued.

#### Scenario: New ticket

- **WHEN** a Ticket is issued
- **THEN** its status is Issued

### Requirement: A ticket is admissible only once and only while Issued

A Ticket SHALL be admissible exactly when its status is Issued and it has no admitted time. A Voided Ticket SHALL NOT be admissible, and a Ticket that has an admitted time SHALL NOT be admissible again. Voiding a Ticket SHALL keep its admitted time, so a refund after entry does not erase that the holder was admitted.

#### Scenario: Issued and not yet admitted

- **WHEN** a Ticket is Issued and has no admitted time
- **THEN** it is admissible

#### Scenario: Already admitted

- **WHEN** a Ticket is Issued and was admitted at 18:32
- **THEN** it is not admissible

#### Scenario: Voided

- **WHEN** a Ticket is Voided and has no admitted time
- **THEN** it is not admissible

#### Scenario: Voided after entry

- **WHEN** a Ticket admitted at 18:32 is Voided by a dispute refund
- **THEN** its status is Voided and its admitted time is still 18:32
