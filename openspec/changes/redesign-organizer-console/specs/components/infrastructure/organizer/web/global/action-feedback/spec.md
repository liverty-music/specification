# Spec Delta

## Purpose

How every control in the organizer console responds to the operator, on a PC and on a phone: touch targets, hover, focus and press feedback, pending actions, confirmation before irreversible actions, unsaved changes and the small motions that confirm what happened.

## ADDED Requirements

### Requirement: Every control is at least 48 × 48 px to touch

Every button, link, tab, checkbox, menu item and navigation item SHALL have a touch target of at least 48 × 48 px, even when its visible shape is smaller, and neighbouring targets SHALL not overlap.

#### Scenario: Copy icon on a phone

- **WHEN** a scanner row shows a 24 px copy icon
- **THEN** the area that responds to a tap is at least 48 × 48 px

### Requirement: Hover, focus and press show a state layer

A control SHALL show an overlay of its content color over its surface when hovered (8 % opacity), when focused from the keyboard (10 %), when pressed (10 %) and while dragged (16 %). Keyboard focus SHALL also show a visible focus ring; focus by pointer click SHALL not leave a ring. A disabled control SHALL show no state layer and SHALL not respond.

#### Scenario: Pointer hover

- **WHEN** an operator moves the pointer over 保存する (save)
- **THEN** an 8 % overlay appears on the button

#### Scenario: Keyboard focus

- **WHEN** an operator reaches 保存する with the Tab key
- **THEN** a 10 % overlay and a focus ring appear

#### Scenario: Pointer click

- **WHEN** an operator clicks 保存する with the mouse
- **THEN** a 10 % overlay shows while pressed and no focus ring remains afterwards

### Requirement: A pending action shows progress in its button and ignores repeats

While an action started from a button is running, the button SHALL show a progress indicator in place of its icon with a label in the progressive form (保存中…, 公開中…), SHALL keep its size, and SHALL ignore further presses. Other controls that would change the same thing SHALL be disabled until the action ends. When the action ends the button SHALL return to its normal state and the result SHALL go to the snackbar.

#### Scenario: Double press on save

- **WHEN** an operator presses 保存する twice within 1 second
- **THEN** one save is sent and the button shows 保存中… with a progress indicator until it finishes

### Requirement: Irreversible actions ask first and name the effect

Before an action that cannot be undone or that affects people outside the console runs, the console SHALL ask for confirmation in a dialog whose title names the action and its object and whose text states the effect; the confirming button SHALL name the action (公開する, 中止する, 取り消す), and the other button SHALL be やめる (keep as is). The dialog SHALL take focus, SHALL keep focus inside it, SHALL close on Escape as やめる, and SHALL return focus to the control that opened it. These actions are: publishing an event (the performers' followers are notified and the event cannot return to draft), 中止 (cancelling) an event or a concert, creating a new share link for an unlisted concert (the previous link stops working), and revoking a scanner or revoking and reissuing it (the device using it stops working).

#### Scenario: Publish asks first

- **WHEN** an operator presses 公開する on a draft event of XX Tour 2026
- **THEN** a dialog asks whether to publish it, says the performers' followers will be notified and that it cannot return to draft, and nothing is published until the operator presses 公開する in the dialog

#### Scenario: Operator changes their mind

- **WHEN** the operator presses やめる or Escape in that dialog
- **THEN** the dialog closes, nothing changes, and focus returns to the 公開する button

#### Scenario: Revoke a scanner

- **WHEN** an operator chooses to revoke 受付1
- **THEN** a dialog says the device using 受付1 will stop working, and 受付1 is revoked only after the operator confirms

### Requirement: Unsaved changes are not lost by leaving

When an operator has changed a form and not saved it, leaving the page through navigation SHALL ask whether to discard the changes, with 破棄する (discard) and 編集を続ける (keep editing); closing or reloading the browser tab SHALL trigger the browser's own leave warning. After a successful save, leaving SHALL not ask.

#### Scenario: Leaving the editor with changes

- **WHEN** an operator edits a concert title and selects Concerts in the navigation without saving
- **THEN** a dialog asks whether to discard the changes, and the page stays when the operator chooses 編集を続ける

#### Scenario: Leaving after saving

- **WHEN** the operator saves and then selects Concerts
- **THEN** the Concerts page opens without a question

### Requirement: Small motions confirm what happened

Copying a value SHALL turn the copy icon into a check mark for 2 seconds and announce コピーしました to screen readers. Changing tabs SHALL slide the tab indicator to the selected tab. A newly issued scanner link SHALL enter its list by fading in and sliding into place. Moving between pages SHALL use a short shared-axis transition. Every motion SHALL take at most 500 ms, and under the system's reduce-motion setting every motion SHALL be replaced by an instant change.

#### Scenario: Copy a link

- **WHEN** an operator presses the copy icon next to a scanner URL
- **THEN** the URL is on the clipboard and the icon shows a check mark for 2 seconds, then returns to the copy icon

#### Scenario: Reduced motion

- **WHEN** the system asks for reduced motion and the operator changes from the Sales tab to the Reception tab
- **THEN** the indicator moves to Reception without animation
