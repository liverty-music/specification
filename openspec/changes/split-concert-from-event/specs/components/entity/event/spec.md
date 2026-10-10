## REMOVED Requirements

### Requirement: Performers of an event

**Reason**: Performing Artists belong to the music kind of event, not to every Event. A fan club event or another future kind would otherwise inherit an Artist relation it may not have.

**Migration**: The rule moves unchanged to the Concert: "A concert has at least one performer" in `components/entity/concert` already states it, and the Concert extends the Event.
