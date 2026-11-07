## ADDED Requirements

### Requirement: An open lottery does not hold up the removal

A lottery entry that is Entered when an Event's cancellation is announced SHALL end soon after it, so that its Void Order no longer blocks the deletion of the Event, even while the sale's window is still open.

#### Scenario: Deleted during the window
- **WHEN** a member cancels the only Event of a Series whose lottery window is open, with one fan Entered and no Paid Order, and an admin uses `Delete` on the Artist concerts screen after the entry has ended
- **THEN** the Event, the Series, the entry and its Void Order no longer exist
