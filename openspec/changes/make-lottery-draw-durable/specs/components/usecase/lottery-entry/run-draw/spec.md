## REMOVED Requirements

### Requirement: Draw a sale's entered entries per ticket stock
**Reason**: RunDraw charged the winners before it recorded the outcome, so a draw that stopped midway drew again in a new random order and could leave a charged fan Lost.
**Migration**: Replaced by LotteryEntryUseCase.Draw, which records the outcome first and charges nothing; OrderUseCase.Issue charges each Won entry and LotteryEntryUseCase.ReleaseCardAuthorization releases the card authorization of each Lost entry.

### Requirement: Capture failure
**Reason**: The draw no longer captures.
**Migration**: A Won entry whose card authorization can no longer be charged is made Lost by OrderUseCase.Issue ("Charge, then issue").

### Requirement: Release failure does not stop the draw
**Reason**: The draw no longer releases.
**Migration**: LotteryEntryUseCase.ReleaseCardAuthorization releases each card authorization on its own and tries again.

### Requirement: The draw issues nothing
**Reason**: Restated by LotteryEntryUseCase.Draw ("Draw a sale without charging").
**Migration**: None.

### Requirement: Each entry's result is reported
**Reason**: Moved with the draw to LotteryEntryUseCase.Draw ("Each entry's result is announced"); a loss from a failed capture is announced by OrderUseCase.Issue.
**Migration**: None.
