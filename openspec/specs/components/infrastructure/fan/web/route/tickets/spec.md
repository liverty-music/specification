# components/infrastructure/fan/web/route/tickets Specification

## Purpose
The fan's tickets screen: the tickets issued to their account, each showing its 特定興行入場券 (covered ticket) face, and the entry QR code the device makes for the tickets entering together, which works without a connection at the venue.

## Requirements

### Requirement: Tickets grouped by event with their face

The screen SHALL list the signed-in fan's tickets grouped by event, nearest event first. Each ticket SHALL show its event's title, date, venue, open and start times, and its covered-ticket face: that resale without the Organizer's consent is prohibited, the eligible person's full name and phone number as the fan's User currently records them, and that no seat is assigned. Each ticket SHALL show its state: 未入場 (not yet entered), 出品中 (listed for official resale), 入場済み (entered) with the admit time, リセール済み (resold) for a ticket voided by its Sold listing, or 無効 (void) for any other voided ticket. The last loaded list SHALL stay viewable without a connection.

#### Scenario: Fan opens their tickets

- **WHEN** a fan with 3 tickets for one event opens the screen
- **THEN** the event is shown once with its 3 tickets, each with the resale notice, the fan's full name and phone number and 未入場

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

The screen, including making the QR code without a connection, SHALL work in the current and previous major versions of Safari on iOS and Chrome on Android.

#### Scenario: iPhone

- **WHEN** a fan opens the screen in Safari on an iPhone with the current iOS
- **THEN** the QR code can be shown

### Requirement: List a ticket for official resale

The screen SHALL read the fan's listings with ResaleListingService.List and, for each event, its sales with TicketSaleService.ListByEvent. For a ticket that is 未入場 and has no Listed listing, whose event's FirstCome TicketType has its resale open, the screen SHALL offer to list it for 公式リセール. Before listing, it SHALL show on one screen: the price 税込, the resale fee of 10%, the refund amount, that the refund goes to the card the fan paid with right after another fan buys the ticket, that the listing closes when admission opens with that date and time, that a sale is not guaranteed and an unsold ticket stays valid, that the listing can be withdrawn until another fan starts buying it, and that a sold ticket becomes invalid. Confirming SHALL call ResaleListingService.Create for that one ticket. A ticket of an event whose TicketType never sold out SHALL offer no listing, and the screen SHALL say that official resale opens only when the event sells out.

#### Scenario: Fan lists a ticket
- **WHEN** a fan with 2 tickets of 5000 yen for a sold-out event lists one of them
- **THEN** the screen shows 5,000円, 手数料 500円 and 返金額 4,500円 before confirming, and after confirming that ticket is shown as 出品中

#### Scenario: Event not sold out
- **WHEN** the fan's event never sold out
- **THEN** the screen offers no listing and says official resale opens only when the event sells out

#### Scenario: Admission opened
- **WHEN** the fan opens the screen after the event's admission window opened
- **THEN** no listing is offered

### Requirement: A listed ticket can be withdrawn and shows its outcome

A ticket shown as 出品中 SHALL offer to withdraw the listing, which calls ResaleListingService.Withdraw; when withdrawing fails with FailedPrecondition, the screen SHALL say that another fan is buying the ticket right now and that it cannot be withdrawn unless that purchase lapses. A ticket shown as リセール済み SHALL show the refund amount and whether the refund has been made, with its date. A listing returned Expired SHALL leave its ticket shown as 未入場.

#### Scenario: Fan withdraws
- **WHEN** the fan withdraws a listed ticket nobody is buying
- **THEN** the ticket is shown as 未入場 again

#### Scenario: Someone is buying it
- **WHEN** the fan withdraws a listed ticket another fan holds in a checkout
- **THEN** the screen says another fan is buying it now and the ticket stays 出品中

#### Scenario: Refund made
- **WHEN** the fan opens the screen after their listed ticket was resold and refunded
- **THEN** the ticket is shown as リセール済み with 返金額 4,500円 and the refund date

#### Scenario: Listing expired
- **WHEN** the fan opens the screen after admission opened and their listing did not sell
- **THEN** the ticket is shown as 未入場 and its QR code can be shown
