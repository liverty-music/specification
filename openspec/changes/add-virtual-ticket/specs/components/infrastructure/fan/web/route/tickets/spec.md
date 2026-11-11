## ADDED Requirements

### Requirement: A ticket opens as a virtual ticket

Tapping a ticket on the screen SHALL open its virtual ticket in a dialog over the list. The virtual ticket SHALL have two sides, and the fan SHALL be able to turn it over by tapping it or with a button below it.

- The front SHALL show the event's cover image, its performers and title, the date, the venue and its prefecture, the open and start times, the ticket's seat type's name and that no seat is assigned. It SHALL hold no personal details, no QR code and no ticket id.
- The back SHALL show the same event and seat items, the eligible person's full name and phone number, a statement that the eligible person's name and contact details were confirmed at the sale, and, for a ticket whose paid transfer without the organizer's consent is prohibited, a statement of that prohibition.

The text of both sides SHALL be selectable and SHALL be read by a screen reader; the side that is turned away SHALL NOT be reachable. The actions the list offers for that ticket (show the QR code, list for official resale, withdraw a listing) and sharing its image SHALL be placed outside the ticket. The virtual ticket SHALL open without a connection from the last loaded list; when the cover image cannot be loaded, the front SHALL be shown without it.

#### Scenario: Fan taps a ticket

- **WHEN** a fan with an S席 ticket that is not yet entered taps it in the list
- **THEN** a dialog shows the front of its virtual ticket with the cover image, the performers, the title, the date, the venue and its prefecture, the open and start times, S席 and 指定なし, without the fan's name or phone number, and the QR code button below the ticket

#### Scenario: Fan turns the ticket over

- **WHEN** the fan taps the virtual ticket of a ticket whose paid transfer without consent is prohibited
- **THEN** the ticket turns to its back, which shows the event and seat items, the fan's full name and phone number, 無断有償譲渡禁止 and 入場資格者の氏名・連絡先確認済み, and the front can no longer be reached until the ticket is turned back

#### Scenario: Tapping a button in the list

- **WHEN** the fan taps a ticket's resale button in the list
- **THEN** the resale action runs and no virtual ticket opens

#### Scenario: Opened in the venue without a connection

- **WHEN** the fan opens a virtual ticket without a connection after loading the screen earlier, and the cover image was never loaded on the device
- **THEN** the virtual ticket opens with every item of the front and without the cover image

#### Scenario: Reading the ticket aloud

- **WHEN** a fan with a screen reader opens a virtual ticket
- **THEN** the screen reader reads the title, the venue, the date and the other items of the front, and after the ticket is turned over, the eligible person's name and the other items of the back

### Requirement: The fan chooses the design of a virtual ticket

A virtual ticket SHALL offer six designs: a standard one and one each for rock, pop, jazz, classical and electronic concerts. A design SHALL change the ticket's colours, typefaces and the treatment of its art, never the items it shows. The fan SHALL be able to pick a design below the ticket, and the ticket SHALL change at once. The device SHALL keep the design picked for each ticket and show the ticket in it when it is opened again; a ticket with no kept design SHALL be shown in the standard design. The choice SHALL stay on the device: another device shows the standard design. Signing out SHALL forget the kept designs.

#### Scenario: Fan picks a design

- **WHEN** the fan picks the rock design below a virtual ticket shown in the standard design
- **THEN** the ticket changes to the rock design at once, showing the same items and the same side

#### Scenario: Design kept on the device

- **WHEN** the fan picks the rock design for a ticket, closes its virtual ticket and opens it again on the same device
- **THEN** the ticket is shown in the rock design

#### Scenario: Design forgotten on sign-out

- **WHEN** the fan signs out after picking a design for a ticket, signs in again on the same device and opens that virtual ticket
- **THEN** the ticket is shown in the standard design

### Requirement: Entry stamps the virtual ticket

A ticket that is 入場済み SHALL show an admission stamp on the front of its virtual ticket, stating 入場済 and the event's date. When the tickets presented by the shown QR code are re-read and every one of them is 入場済み, the screen SHALL close the code and open the virtual ticket of the first of them in the list with the stamp being pressed onto its front. When some of them are still not entered, the code SHALL stay open for the rest. A device SHALL play the pressing animation once per ticket: the first time it shows that ticket's virtual ticket as 入場済み, including a ticket admitted while the fan was not watching. Later openings, and every opening when the fan has asked the device to reduce motion, SHALL show the stamp at rest. Signing out SHALL forget which stamps the device has played.

#### Scenario: Admitted while the code is shown

- **WHEN** the fan shows the code for 2 tickets, both are admitted, and the device has a connection
- **THEN** the code closes and the first ticket's virtual ticket opens, and a stamp with 入場済 and the event's date is pressed onto its front

#### Scenario: Only some admitted

- **WHEN** the fan shows the code for 3 tickets and 1 of them is admitted
- **THEN** the code stays open for the other 2 and no virtual ticket opens

#### Scenario: Admitted without the code on screen

- **WHEN** the fan's ticket was admitted while the fan's device had no connection, and the fan later opens its virtual ticket with a connection
- **THEN** the stamp is pressed onto it with the pressing animation

#### Scenario: Opened again

- **WHEN** the fan opens a virtual ticket whose stamp animation the device has already played
- **THEN** the stamp is shown at rest without the animation

#### Scenario: Reduced motion

- **WHEN** the fan has asked the device to reduce motion and is admitted while the code is shown
- **THEN** the virtual ticket opens with the stamp at rest

#### Scenario: Signed out and in again

- **WHEN** the fan signs out after the stamp of an entered ticket was played, signs in again on the same device and opens that virtual ticket
- **THEN** the stamp is pressed onto it with the pressing animation

#### Scenario: Not yet entered

- **WHEN** the fan opens the virtual ticket of a ticket that is 未入場
- **THEN** it shows no stamp

### Requirement: The fan can share an image of a virtual ticket without personal details

From a virtual ticket, the fan SHALL be able to share an image of it. The image SHALL be the ticket's front in the design the ticket is shown in, and SHALL contain no full name, no phone number, no admission stamp, no QR code and no ticket id. Making the image SHALL never change the virtual ticket the fan is looking at. When the cover image cannot be loaded, the image SHALL be made without it. The image SHALL be handed to the device's share sheet as a file; where the browser cannot share files, it SHALL be downloaded instead.

#### Scenario: Sharing from a phone

- **WHEN** the fan taps 画像を共有 on a virtual ticket on a phone
- **THEN** the share sheet opens with an image of the ticket's front, which shows neither the fan's name nor their phone number

#### Scenario: Shared after entry

- **WHEN** the fan shares the image of a virtual ticket that is 入場済み
- **THEN** the image shows no stamp

#### Scenario: Sharing without the cover image

- **WHEN** the fan taps 画像を共有 without a connection on a virtual ticket whose cover image was never loaded on the device
- **THEN** the share sheet opens with the image of the front without the cover image

#### Scenario: Browser without file sharing

- **WHEN** the fan taps 画像を共有 in a desktop browser that cannot share files
- **THEN** the image is downloaded

## MODIFIED Requirements

### Requirement: Supported browsers

The screen, including making the QR code without a connection, opening a virtual ticket, its admission stamp and sharing its image, SHALL work in the current and previous major versions of Safari on iOS and Chrome on Android.

#### Scenario: iPhone

- **WHEN** a fan opens the screen in Safari on an iPhone with the current iOS
- **THEN** the QR code can be shown

#### Scenario: Virtual ticket on an iPhone

- **WHEN** a fan opens a virtual ticket that is 入場済み in Safari on an iPhone with the current iOS and shares its image
- **THEN** the virtual ticket shows the stamp and the share sheet receives the image of its front with the cover image

#### Scenario: Virtual ticket on an Android phone

- **WHEN** a fan opens a virtual ticket that is 入場済み in Chrome on an Android phone with the current Android and shares its image
- **THEN** the virtual ticket shows the stamp and the share sheet receives the image of its front with the cover image
