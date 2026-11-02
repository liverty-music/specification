## REMOVED Requirements

### Requirement: Each admitted ticket is reported
**Reason**: Ticket.Admit announces each Ticket it admits together with the admission (components/entity/ticket/admit), so the usecase no longer sends a signal.
**Migration**: Product analytics receives the "ticket admitted" signal from Ticket.Admit's announcement. A failure to announce now fails Ticket.Admit, so Admit fails with Unavailable as for any Ticket.Admit failure and staff scan again.
