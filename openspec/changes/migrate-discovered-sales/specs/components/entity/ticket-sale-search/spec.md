# Spec Delta

## Purpose

A Ticket Sale Search records when a Series was last searched for published ticket sales, so that discovery searches each series at most once in a given interval, whether or not that search found anything.

| attribute | meaning | constraint |
|---|---|---|
| series | The series that was searched | required; one per series |
| searched time | When the series was last searched successfully | required, an absolute instant |

```mermaid
erDiagram
    Series ||--o| TicketSaleSearch : "was last searched"
```

## ADDED Requirements

### Requirement: Searched time is not in the future

A ticket sale search's searched time SHALL NOT be after the current time.

#### Scenario: Future searched time
- **WHEN** a ticket sale search carries a searched time one hour from now
- **THEN** the ticket sale search is invalid
