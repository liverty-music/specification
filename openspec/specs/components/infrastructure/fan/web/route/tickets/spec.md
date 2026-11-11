# components/infrastructure/fan/web/route/tickets Specification

## Purpose
The fan's tickets screen: the tickets issued to their account, each showing its 特定興行入場券 (covered ticket) face, and the entry QR code the device makes for the tickets entering together, which works without a connection at the venue.

## Requirements

### Requirement: Tickets grouped by event with their face

The screen SHALL list the signed-in fan's tickets grouped by event, nearest event first. Each ticket SHALL show its event's title, date, venue, open and start times, its seat type's name, and its covered-ticket face: that resale without the Organizer's consent is prohibited, the eligible person's full name and phone number as the fan's User currently records them, and that no seat is assigned. Each ticket SHALL show its state: 未入場 (not yet entered), 出品中 (listed for official resale), 入場済み (entered) with the admit time, リセール済み (resold) for a ticket voided by its Sold listing, or 無効 (void) for any other voided ticket. The last loaded list SHALL stay viewable without a connection.

#### Scenario: Fan opens their tickets

- **WHEN** a fan with 3 S席 tickets for one event opens the screen
- **THEN** the event is shown once with its 3 tickets, each with S席, the resale notice, the fan's full name and phone number and 未入場

#### Scenario: Fan corrected their phone number

- **WHEN** the fan changed their phone number after the tickets were issued and opens the screen with a connection
- **THEN** each ticket's face shows the new phone number

#### Scenario: Refunded ticket

- **WHEN** one of the fan's tickets was voided by a refund
- **THEN** it is shown as 無効 and offers no QR code

#### Scenario: Resold ticket

- **WHEN** one of the fan's tickets was bought by another fan through official resale
- **THEN** it is shown as リセール済み and offers no QR code

#### Scenario: No signal in the venue

- **WHEN** the fan opens the screen without a connection after loading it earlier
- **THEN** the tickets loaded earlier are shown

### Requirement: The entry device is chosen once and moves only when the fan asks

The entry device is the device whose public key is the fan's WalletPublicKey; only it can make an entry QR code that is admitted. When the fan opens or reloads the screen with a connection, the screen SHALL read the fan's WalletPublicKey with WalletPublicKeyUseCase.Get and compare it with this device's key, and SHALL change nothing on the server except in these cases:

- When the fan has no WalletPublicKey, the screen SHALL create a key pair on the device if it has none, whose private key cannot be read out of the device by the page, and register its public key with WalletPublicKeyUseCase.Register, asking nothing of the fan.
- When the fan's WalletPublicKey belongs to another device, the screen SHALL say that the entry QR code is set to another device and offer to use this device instead. Only when the fan confirms SHALL it create a key pair if needed and register its public key, and then say that the QR code now works on this device only.

When the fan's WalletPublicKey cannot be read although the screen has a connection, the screen SHALL go by the result of its last successful check. When registering after the fan confirmed fails, the device SHALL stay a device that is not the entry device and the screen SHALL say so and offer to try again. Without a connection, the screen SHALL offer the QR code only on a device that was the entry device at its last successful check, and SHALL NOT offer to use this device instead.

#### Scenario: First visit on a phone

- **WHEN** a fan with no entry device opens the screen on a phone with a connection
- **THEN** the phone becomes the entry device without asking, and can show the QR code offline from then on

#### Scenario: Viewing on another device

- **WHEN** a fan whose entry device is their phone opens the screen on a PC with a connection
- **THEN** the tickets are shown, the screen says the QR code is set to another device and offers no QR code, and the phone stays the entry device

#### Scenario: Moving to a new phone

- **WHEN** the fan opens the screen on a new phone and confirms using this device
- **THEN** the new phone becomes the entry device, the screen says the QR code now works on this device only, and codes from the old phone are refused at the venue

#### Scenario: Reloading on the entry device

- **WHEN** the fan reloads the screen on the entry device
- **THEN** nothing is registered and the QR code is offered

#### Scenario: Key cannot be read

- **WHEN** the entry device opens the screen with a connection and reading the fan's WalletPublicKey fails
- **THEN** the QR code is still offered, as at the last check

#### Scenario: Moving fails

- **WHEN** the fan confirms using this device and registering fails
- **THEN** the screen says the move failed and offers to try again, and offers no QR code

#### Scenario: Other device without a connection

- **WHEN** a device that was told the QR code is set to another device opens the screen without a connection
- **THEN** it says so again and offers neither the QR code nor to use this device

#### Scenario: Not prepared and offline

- **WHEN** a fan opens the screen for the first time on a phone without a connection
- **THEN** the screen says it needs a connection once before the QR code can be shown

### Requirement: One QR code for the tickets entering together

For an event with tickets that are not yet entered, the screen SHALL offer to show the entry QR code. The code SHALL present every not-yet-entered ticket of the event, up to 10, with no way to leave one out, because the fan and their companions enter together, and SHALL state how many people it admits. The device SHALL make a new code every 15 seconds while it is shown, signed with its private key, with or without a connection, and SHALL never show a code older than 15 seconds. While the code is shown the screen SHALL keep the display awake, and stop doing so when the code is closed.

#### Scenario: Whole group

- **WHEN** the fan shows the code for an event with 3 not-yet-entered tickets
- **THEN** one QR code stating 3名 is shown and it changes every 15 seconds

#### Scenario: No ticket left out

- **WHEN** the fan opens the code for an event with 3 not-yet-entered tickets
- **THEN** all 3 are presented and the screen offers no way to leave one out

#### Scenario: Shown without a connection

- **WHEN** the fan shows the code in the venue without a connection
- **THEN** the code is shown and changes every 15 seconds

#### Scenario: Screen stays on

- **WHEN** the code has been shown for 2 minutes without the fan touching the screen
- **THEN** the display has stayed on

#### Scenario: After entry

- **WHEN** the fan's tickets are admitted while the code is shown and the device has a connection
- **THEN** the screen shows them as 入場済み with the admit time

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

### Requirement: List a ticket for official resale

The screen SHALL read the fan's listings with ResaleListingService.List and, for each event, its sales with TicketSaleService.ListByEvent. For a ticket that is 未入場 and has no Listed listing, whose TicketStock has its resale open, the screen SHALL offer to list it for 公式リセール. Before listing, it SHALL show on one screen: the price 税込, the resale fee of 10%, the refund amount, that the refund goes to the card the fan paid with right after another fan buys the ticket, that the listing closes at the resale deadline (12:00 Japan time on the event's day or 3 hours before the start time, whichever is earlier) with that date and time, that a sale is not guaranteed and an unsold ticket stays valid, that the listing can be withdrawn until a draw allocates it or listing closes, and that a sold ticket becomes invalid. Confirming SHALL call ResaleListingService.Create for that one ticket. A ticket whose TicketStock is not sold out SHALL offer no listing, and the screen SHALL say that official resale opens only when the seat type sells out for the event.

#### Scenario: Fan lists a ticket
- **WHEN** a fan with 2 S席 tickets of 5000 yen for an event whose S席 sold out lists one of them
- **THEN** the screen shows 5,000円, 手数料 500円 and 返金額 4,500円 before confirming, and after confirming that ticket is shown as 出品中

#### Scenario: Event not sold out
- **WHEN** the seat type of the fan's tickets never sold out for the event
- **THEN** the screen offers no listing and says official resale opens only when the seat type sells out

#### Scenario: Admission opened
- **WHEN** the fan opens the screen after the event's admission window opened
- **THEN** no listing is offered

### Requirement: A listed ticket can be withdrawn until a draw allocates it or listing closes

A ticket shown as 出品中 SHALL offer to withdraw the listing, which calls ResaleListingService.Withdraw; a listing can be withdrawn until a draw allocates it or listing closes. When withdrawing fails with FailedPrecondition, the screen SHALL say that the listing can no longer be withdrawn because a draw allocated it or listing has closed, and SHALL read the fan's listings again. A ticket shown as リセール済み SHALL show the refund amount and whether the refund has been made, with its date. A listing returned Expired SHALL leave its ticket shown as 未入場.

#### Scenario: Fan withdraws
- **WHEN** the fan withdraws a listed ticket before listing closes
- **THEN** the ticket is shown as 未入場 again

#### Scenario: Listing already closed
- **WHEN** the fan withdraws a listed ticket after a draw allocated it or listing closed
- **THEN** the screen says the listing can no longer be withdrawn and shows the ticket as the listings read again say

#### Scenario: Refund made
- **WHEN** the fan opens the screen after their listed ticket was resold and refunded
- **THEN** the ticket is shown as リセール済み with 返金額 4,500円 and the refund date

#### Scenario: Listing expired
- **WHEN** the fan opens the screen after admission opened and their listing did not sell
- **THEN** the ticket is shown as 未入場 and its QR code can be shown

### Requirement: A ticket opens as a virtual ticket

Tapping a ticket on the screen SHALL open its virtual ticket in a dialog over the list. The virtual ticket SHALL have two sides, and the fan SHALL be able to turn it over by tapping it or with a button below it.

- The front SHALL show the event's cover image, its performers and title, the date, the venue and its prefecture, the open and start times, the ticket's seat type's name and that no seat is assigned. It SHALL hold no personal details, no QR code and no ticket id.
- The back SHALL show the same event and seat items, the eligible person's full name and phone number, a statement that the eligible person's name and contact details were confirmed at the sale, and a statement that paid transfer without the organizer's consent is prohibited.

The text of both sides SHALL be selectable and SHALL be read by a screen reader; the side that is turned away SHALL NOT be reachable. The actions the list offers for that ticket (show the QR code, list for official resale, withdraw a listing) and sharing its image SHALL be placed outside the ticket. The virtual ticket SHALL open without a connection from the last loaded list; when the cover image cannot be loaded, the front SHALL be shown without it.

#### Scenario: Fan taps a ticket

- **WHEN** a fan with an S席 ticket that is not yet entered taps it in the list
- **THEN** a dialog shows the front of its virtual ticket with the cover image, the performers, the title, the date, the venue and its prefecture, the open and start times, S席 and 指定なし, without the fan's name or phone number, and the QR code button below the ticket

#### Scenario: Fan turns the ticket over

- **WHEN** the fan taps the virtual ticket of a ticket
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
