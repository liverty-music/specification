## REMOVED Requirements

### Requirement: Each expired checkout is reported
**Reason**: Checkout.Release announces a Checkout it makes Expired together with the change (components/entity/checkout/release), so the usecase no longer sends a signal.
**Migration**: Product analytics receives the "checkout expired" signal from Checkout.Release's announcement. A failure to announce now fails the release of that Checkout, which stays Held and is tried again on the next run.
