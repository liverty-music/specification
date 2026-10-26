## REMOVED Requirements

### Requirement: Draw a sale
**Reason**: RunDraw charged winners before it recorded the outcome, so a draw that stopped midway could draw again and leave a charged fan Lost.
**Migration**: Replaced by LotteryEntryUseCase.Draw, which records the outcome first; OrderUseCase.Issue charges each Won entry and CardAuthorizationUseCase.Release releases the others.

### Requirement: Capture failure
**Reason**: The draw no longer captures.
**Migration**: A capture that cannot succeed makes the entry Lost in OrderUseCase.Issue ("Charge, then issue").

### Requirement: Release failure does not stop the draw
**Reason**: The draw no longer releases.
**Migration**: CardAuthorizationUseCase.Release releases and retries each card authorization on its own.

### Requirement: The draw issues nothing
**Reason**: Restated by LotteryEntryUseCase.Draw ("Draw a sale without charging").
**Migration**: None.

### Requirement: Each entry's result is reported
**Reason**: Moved with the draw to LotteryEntryUseCase.Draw; a loss from a failed capture is reported by OrderUseCase.Issue.
**Migration**: None.
