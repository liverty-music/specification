## Purpose

Lets a fan view the tickets issued to their account in an in-app wallet, showing each ticket's event details, entry status, and the covered-ticket face conditions rendered on the credential they present at the gate.

## ADDED Requirements

### Requirement: Ticket wallet renders the ticket and its covered-ticket face

The system SHALL let an authenticated fan view the **tickets issued to their
account** (from ⑤): event details, each ticket's **entry status** (not-yet-entered
/ entered), and the **covered-ticket (特定興行入場券) face conditions** defined by ⑤
— (i) the resale-without-organizer-consent-prohibited statement, (ii) date/venue +
seat-or-eligible-person, (iii) the 本人確認 (name) — rendered on the presented
credential so the ticket satisfies the "stated on its face" test where the holder
actually presents it. ⑤ owns the face **content**; ⑥ owns **rendering** it.

#### Scenario: Fan views their ticket with the covered-ticket face

- **WHEN** an authenticated fan opens a ticket in their wallet
- **THEN** they see event details, entry status, and the covered-ticket face conditions (resale-prohibited notice + date/venue/seat-or-eligible-person + 本人確認) rendered on the presented credential
