## REMOVED Requirements

### Requirement: A new association is announced
**Reason**: Organizer.AssociateArtist announces a new link together with storing it (components/entity/organizer/associate-artist), so the usecase no longer announces.
**Migration**: Product analytics receives the "artist associated" signal from Organizer.AssociateArtist's announcement. A failure to announce now fails AssociateArtist and stores no link.
