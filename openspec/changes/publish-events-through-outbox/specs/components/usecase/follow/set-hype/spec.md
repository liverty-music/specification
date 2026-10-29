## REMOVED Requirements

### Requirement: SetHype reports each hype level set
**Reason**: Follow.SetHype announces a changed level together with the change (components/entity/follow/set-hype), so the usecase no longer sends a signal, and setting the level a Follow already has is not reported.
**Migration**: Product analytics receives the "hype set" signal from that announcement, for changes only. A failure to announce now fails SetHype and leaves the level unchanged.
