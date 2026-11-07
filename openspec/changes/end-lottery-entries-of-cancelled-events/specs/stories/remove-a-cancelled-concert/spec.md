## ADDED Requirements

### Requirement: An open lottery does not hold up the removal

An Entered lottery entry of a cancelled Event SHALL end soon after the cancellation, so that once its card authorization is released it no longer blocks the deletion of the Event, even while the sale's window is still open.

#### Scenario: Deleted during the window
- **WHEN** a member cancels the only Event of a Series whose lottery window is open, with one fan Entered and no Paid Order, and an admin uses `Delete` on the Artist concerts screen after the entry has ended
- **THEN** the Event, the Series, the entry and its Void Order no longer exist
