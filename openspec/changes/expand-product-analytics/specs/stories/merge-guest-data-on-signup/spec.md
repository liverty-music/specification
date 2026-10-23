## ADDED Requirements

### Requirement: The merge reports how many follows it carried over

When the merge of a guest's data into the new account finishes, the fan app SHALL send one usage analytics event under the new account with the number of artist follows the merge carried over, including zero.

#### Scenario: Guest with five follows signs up
- **WHEN** a guest who follows 5 artists signs up and the merge finishes
- **THEN** one event is sent for the new account with a count of 5
