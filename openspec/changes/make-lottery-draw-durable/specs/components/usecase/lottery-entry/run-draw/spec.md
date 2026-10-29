## REMOVED Requirements

### Requirement: Draw a sale's entered entries per ticket stock
**Reason**: RunDraw charged the winners before it recorded the outcome, so a draw that stopped midway drew again in a new random order and could leave a charged fan Lost.
**Migration**: Replaced by LotteryEntryUseCase.Draw, which records the outcome first and charges nothing; OrderUseCase.Issue charges each Won entry and OrderUseCase.ReleaseCardAuthorization releases the card authorization of each Lost entry.

### Requirement: Capture failure
**Reason**: The draw no longer captures.
**Migration**: A Won entry whose card authorization can no longer be charged is made Lost, with the lost reason "card could not be charged", by OrderUseCase.Issue ("Charge, then issue") through LotteryEntry.RevertWin.

### Requirement: Release failure does not stop the draw
**Reason**: The draw no longer releases.
**Migration**: OrderUseCase.ReleaseCardAuthorization releases each card authorization on its own and tries again.

### Requirement: The draw issues nothing
**Reason**: Restated by LotteryEntryUseCase.Draw ("Draw a sale without charging").
**Migration**: None.
