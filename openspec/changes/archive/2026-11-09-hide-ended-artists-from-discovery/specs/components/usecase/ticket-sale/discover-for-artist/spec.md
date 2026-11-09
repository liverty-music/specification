# Spec Delta

## ADDED Requirements

### Requirement: Artists whose activity has ended are not searched

DiscoverForArtist SHALL return 0 without searching, storing or recording anything when the artist's activity_ended is true.

#### Scenario: Ended artist
- **WHEN** DiscoverForArtist is called for an artist whose activity_ended is true and who has a tracked series with an upcoming event
- **THEN** TicketSale.SearchPublishedSales is not called, nothing is stored or recorded, and DiscoverForArtist returns 0
