## REMOVED Requirements

### Requirement: Start an entry while the window is open
**Reason**: There is no Draft to start; the fan authorizes their card for a ticket count and confirms.
**Migration**: The checks move to LotteryEntryUseCase.AuthorizeCard; LotteryEntryService.Start is removed.

### Requirement: Verification gate
**Reason**: Start is removed.
**Migration**: Moved unchanged to LotteryEntryUseCase.AuthorizeCard.

### Requirement: Record the referral code the entry started with
**Reason**: Start is removed and the Referral entity is folded into the purchases.
**Migration**: AuthorizeCard takes the code onto the card authorization, and Confirm stores it on the entry.
