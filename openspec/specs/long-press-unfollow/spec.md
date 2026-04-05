# Capability: Long-Press Unfollow

## Purpose

Enable touch device users to unfollow an artist via a long-press gesture on an artist row, presenting an unfollow confirmation BottomSheet before executing the action.

## Requirements

### Requirement: Long-press gesture triggers unfollow confirmation on touch devices

On touch devices (`pointer: coarse`), the system SHALL detect a 500ms long-press on an artist row
and open an unfollow confirmation BottomSheet for that artist. The BottomSheet SHALL display the
artist name, a danger-styled "Unfollow" button, and a cancel option. Desktop devices (`pointer: fine`)
SHALL NOT attach the long-press listener; they retain the existing trash icon column.

#### Scenario: Long-press opens unfollow sheet

- **WHEN** user holds a pointer down on an artist row for 500ms on a touch device
- **THEN** an unfollow confirmation BottomSheet opens showing the artist's name and an Unfollow button

#### Scenario: Long-press cancelled by movement

- **WHEN** user presses down on an artist row and moves the pointer more than 10px before 500ms elapses
- **THEN** the long-press timer is cancelled and no BottomSheet opens

#### Scenario: Long-press cancelled by pointer up

- **WHEN** user releases the pointer before 500ms elapses
- **THEN** the long-press timer is cancelled and no BottomSheet opens

#### Scenario: Long-press cancelled by pointercancel

- **WHEN** the browser fires a pointercancel event (e.g. OS text-selection or scroll takeover) before 500ms elapses
- **THEN** the long-press timer is cancelled and no BottomSheet opens

#### Scenario: Unfollow confirmed via BottomSheet

- **WHEN** user taps the "Unfollow" button in the BottomSheet
- **THEN** the BottomSheet closes and the existing unfollow flow executes (optimistic removal + undo toast)

#### Scenario: Unfollow cancelled via BottomSheet

- **WHEN** user taps the cancel button or dismisses the BottomSheet without confirming
- **THEN** the BottomSheet closes and the artist remains in the list

#### Scenario: No long-press listener on desktop

- **WHEN** the page loads on a device where `pointer: fine` matches
- **THEN** no long-press listener is attached to artist rows and the trash icon column remains visible
