## Purpose

ConcertCreationUseCase.RemoveEmptyDiscoveredSeries removes, once a day, every discovered Series that is at least a day old and has no Event, no ConcertCandidate and no TicketSale: a Series discovery created whose events were all rejected, merged away or never stored.

```mermaid
sequenceDiagram
autonumber
participant UC as ConcertCreationUseCase.RemoveEmptyDiscoveredSeries
participant Series
Note over UC: runs once a day
UC->>Series: DeleteOrphaned "created more than a day ago"
break DeleteOrphaned fails
  Note over UC: fail, the next day's run removes them
end
```

## ADDED Requirements

### Requirement: Empty discovered Series are removed daily

Once a day, RemoveEmptyDiscoveredSeries SHALL remove every discovered Series created more than a day before the run that has no Event, no ConcertCandidate and no TicketSale (Series.DeleteOrphaned). A run SHALL NOT overlap a CreateFromDiscovered batch: it waits until the batch being processed has ended (see CreateFromDiscovered, "One batch at a time"), since a batch can empty an old Series with a Merge and then store more Events under it. When the removal fails, the run SHALL fail, and the next day's run SHALL remove them.

#### Scenario: Series emptied by a rejection
- **WHEN** the only ConcertCandidate of a discovered Series created two days ago was rejected
- **THEN** the day's run removes that Series

#### Scenario: Series of a merged event
- **WHEN** a Merge removed the only Event of a discovered Series created two days ago that has no TicketSale
- **THEN** the day's run removes that Series

#### Scenario: Batch being processed
- **WHEN** the day's run is due while a CreateFromDiscovered batch is being processed
- **THEN** the run waits until that batch has ended

#### Scenario: Removal fails
- **WHEN** DeleteOrphaned fails with Unavailable
- **THEN** the run fails and the next day's run removes the Series
