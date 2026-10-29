# Spec Delta

## REMOVED Requirements

### Requirement: The code of a Held checkout is set

**Reason**: The referral code is the Order's, set when the Order is created and never changed, for a checkout as for a lottery entry.
**Migration**: Checkout.GetOrCreateHeld takes the ReferralCode and stores it on the new Order; a fan who follows another link during a hold keeps the code they started with.
