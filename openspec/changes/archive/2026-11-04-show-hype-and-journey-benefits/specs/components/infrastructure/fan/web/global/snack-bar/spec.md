## ADDED Requirements

### Requirement: At most three snacks are shown at once

In the fan app, when a new snack would make more than three snacks visible, the snack bar SHALL first dismiss the oldest visible snack that dismisses on its own, so the newest three remain, passing over a snack whose dismissal commits something the fan can still undo (such as an unfollow's undo) while another snack can be dismissed instead. A snack that stays until the fan acts, such as the app update snack, SHALL neither count toward the three nor be dismissed by a newer snack. A snack that a sender marks as replacing its own earlier snack SHALL take that snack's place instead of being added.

#### Scenario: Fourth snack

- **WHEN** three snacks that dismiss on their own are visible and a fourth snack is shown
- **THEN** the oldest of the three is dismissed and the newest three are visible

#### Scenario: Update snack stays

- **WHEN** the app update snack and three other snacks are visible and a new snack is shown
- **THEN** the update snack stays, the oldest of the other three is dismissed, and the update snack plus three others are visible

#### Scenario: An undo window is kept

- **WHEN** a fan unfollows an artist and, while its undo snack is visible, changes the hype levels of three other artists
- **THEN** the undo snack stays and the oldest hype snack is dismissed

#### Scenario: Replacing an earlier snack

- **WHEN** a screen shows a snack for an artist and then a new snack that replaces its earlier snack for the same artist
- **THEN** only the new snack is visible for that artist
