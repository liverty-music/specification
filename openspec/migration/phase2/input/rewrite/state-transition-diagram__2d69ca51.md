<!-- spec: state-transition-diagram | target: stories/merge-guest-data-on-signup | flags: CLASSNAME | new_name: Guest data accumulates before signup and clears after merge -->

### Requirement: Guest data accumulates before signup and clears after merge

Guest state SHALL be a simple data bag tracking ephemeral data accumulated before the user creates an account (followed artists and home location). On signup the data is merged into the backend, then cleared. There are no discrete named states, only data mutations. The key invariant is that `guest/follow` is idempotent — a duplicate `artistId` is a no-op.

| Action              | Effect                                                  | Where                 |
|---------------------|---------------------------------------------------------|-----------------------|
| `guest/follow`      | Append `{ artistId, name }` to follows (skip if exists) | discovery-route       |
| `guest/unfollow`    | Remove entry by artistId                                | my-artists-route      |
| `guest/setUserHome` | Set home ISO-3166-2 code                                | area-selector (modal) |
| `guest/clearAll`    | Reset follows to `[]` and home to `null`                | welcome-route, merge  |

#### Scenario: guest/follow is idempotent

- **WHEN** `guest/follow` is dispatched with an `artistId` already present in the follows list
- **THEN** the list SHALL be unchanged (no duplicate entry)

#### Scenario: guest/follow appends a new artist

- **WHEN** `guest/follow` is dispatched from `discovery-route` with a new `artistId`
- **THEN** `{ artistId, name }` SHALL be appended to the follows list

#### Scenario: guest/unfollow removes an entry

- **WHEN** `guest/unfollow` is dispatched with an `artistId` present in the list
- **THEN** the matching entry SHALL be removed by `artistId`

#### Scenario: guest/setUserHome sets the home code

- **WHEN** `guest/setUserHome` is dispatched from the area selector
- **THEN** the guest home SHALL be set to the given ISO-3166-2 code

#### Scenario: guest/clearAll resets on merge or welcome

- **WHEN** `guest/clearAll` is dispatched (from `welcome-route` or after a signup merge)
- **THEN** follows SHALL be reset to `[]` and home to `null`
