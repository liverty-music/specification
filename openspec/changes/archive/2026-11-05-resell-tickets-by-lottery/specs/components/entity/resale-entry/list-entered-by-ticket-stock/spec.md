# Spec Delta

## Purpose

Lists the Entered ResaleEntries of one TicketStock with their Orders and card authorization expiry times, the candidates of a draw.

## ADDED Requirements

### Requirement: Candidates of a draw

ListEnteredByTicketStock SHALL return every Entered ResaleEntry whose Order names the given TicketStock, each with its Order and its card authorization's expiry time, and SHALL return an empty list when there is none. Won, Lost and Lapsed entries SHALL NOT be returned.

#### Scenario: Mixed states
- **WHEN** a stock has two Entered entries, one Won and one Lapsed
- **THEN** the two Entered entries are returned

#### Scenario: No candidates
- **WHEN** the stock has no Entered entry
- **THEN** the list is empty
