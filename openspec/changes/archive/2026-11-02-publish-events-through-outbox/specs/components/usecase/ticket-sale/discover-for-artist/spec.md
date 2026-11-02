## ADDED Requirements

### Requirement: Only a newly created sale is counted

DiscoverForArtist SHALL return the number of sales that TicketSale.UpsertDiscovered reports as Inserted. A sale reported as Updated or Skipped SHALL NOT be counted. TicketSale.UpsertDiscovered announces each created sale together with it, so DiscoverForArtist requests no announcement.

#### Scenario: New sale
- **WHEN** a discovered sale is created
- **THEN** it counts towards the returned number

#### Scenario: Known sale discovered again
- **WHEN** a discovered sale updates a sale already known
- **THEN** it is not counted

#### Scenario: Sale cannot be stored with its announcement
- **WHEN** TicketSale.UpsertDiscovered fails with Unavailable for one of three sales
- **THEN** that sale is not stored and not counted, and the other two are stored

## REMOVED Requirements

### Requirement: Only a newly created sale is announced
**Reason**: TicketSale.UpsertDiscovered announces a created sale together with its creation (components/entity/ticket-sale/upsert-discovered), so DiscoverForArtist no longer requests the announcement, and a stored sale is never left unannounced.
**Migration**: Replaced by "Only a newly created sale is counted". TicketSaleAnnouncementUseCase.AnnounceDiscoveredSale runs on the announcement of TicketSale.UpsertDiscovered. A sale whose announcement cannot be recorded is no longer stored; like any sale that cannot be stored, it is skipped.
