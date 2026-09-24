<!-- spec: state-transition-diagram | target: stories/merge-guest-data-on-signup | flags: CLASSNAME | new_name: Guest data accumulates before signup and clears after merge -->

### Requirement: Guest data accumulates before signup and clears after merge

Guest state SHALL be a simple data bag tracking ephemeral data accumulated before the user creates an account (followed artists and home location). On signup the data is merged into the backend, then cleared. There are no discrete named states, only data mutations. The key invariant is that following an artist as a guest is idempotent — following an artist a second time is a no-op.

| Action                 | Effect                                                  | Origin                 |
|------------------------|-----------------------------------------------------------|-------------------------|
| Follow an artist       | Append `{ artistId, name }` to follows (skip if exists) | the discovery page      |
| Unfollow an artist     | Remove entry by artistId                                | the followed-artists page |
| Set home area          | Set home ISO-3166-2 code                                | the area selector (modal) |
| Clear all guest data   | Reset follows to `[]` and home to `null`                | the welcome page, or after a signup merge |

#### Scenario: guest/follow is idempotent

- **WHEN** following an artist already present in the follows list
- **THEN** the list SHALL be unchanged (no duplicate entry)

#### Scenario: guest/follow appends a new artist

- **WHEN** a new artist is followed from the discovery page
- **THEN** `{ artistId, name }` SHALL be appended to the follows list

#### Scenario: guest/unfollow removes an entry

- **WHEN** an artist present in the list is unfollowed
- **THEN** the matching entry SHALL be removed by `artistId`

#### Scenario: guest/setUserHome sets the home code

- **WHEN** the home area is set from the area selector
- **THEN** the guest home SHALL be set to the given ISO-3166-2 code

#### Scenario: guest/clearAll resets on merge or welcome

- **WHEN** all guest data is cleared (from the welcome page or after a signup merge)
- **THEN** follows SHALL be reset to `[]` and home to `null`
