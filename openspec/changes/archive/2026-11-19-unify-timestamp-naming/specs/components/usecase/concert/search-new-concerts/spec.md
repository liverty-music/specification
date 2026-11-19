# Spec Delta

## MODIFIED Requirements

### Requirement: The search is recorded

Before the external search, SearchNewConcerts SHALL restart the Artist's ConcertSearch as pending (ConcertSearch.Upsert), and SHALL fail without searching when that cannot be recorded. When the search ends with an error the status SHALL become failed; otherwise completed. When new concerts are handed on, SearchNewConcerts SHALL record the discovery (ConcertSearch.MarkFound); a failure to update the status or record the discovery SHALL NOT change the result.

#### Scenario: Productive search
- **WHEN** the search hands on two new concerts
- **THEN** the ConcertSearch is completed and its last find time is now

#### Scenario: Nothing new
- **WHEN** the search finds only known concerts
- **THEN** the ConcertSearch is completed and its last find time is unchanged

#### Scenario: External search fails
- **WHEN** the external search fails with an error
- **THEN** the ConcertSearch is failed and SearchNewConcerts fails
