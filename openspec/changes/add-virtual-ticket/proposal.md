## Why

A fan's ticket on the tickets screen is a list item with the 特定興行入場券 (covered ticket) face as plain text. Nothing marks the moment of entry, and the fan has nothing to keep or show after the concert. A virtual ticket gives each ticket a collectible face built from the concert's cover image, marks entry with an admission stamp when the existing QR admission completes, and lets the fan share an image of it without their personal details.

The owner chose this design in the html-plan review of 2026-11-09 to 11-10, after a spike on Chrome 157 and WebKit 27.2 (results in design.md).

## What Changes

- Tapping a ticket on the tickets screen opens its virtual ticket in a dialog. The ticket has two sides and turns over at a tap. The front is the keepsake: the cover image as art under a holographic foil, the performers, the event title, the date, the venue and its prefecture, the open and start times, the seat type and that no seat is assigned. The back is the 特定興行入場券 face: the same items with the eligible person's full name and phone number, the statement that their name and contact details were confirmed at the sale, and the statement that paid transfer without the organizer's consent is prohibited. The actions (show the QR code, share, list for resale) sit outside the ticket. The list itself does not change.
- The fan picks one of six designs for each ticket (standard, rock, pop, jazz, classical, electronic). The device keeps the choice; it is not sent to the server.
- When a ticket is admitted while its QR code is shown, the code closes and the virtual ticket opens with an admission stamp animation (入場済, ringed by the event's date). A ticket admitted while the fan was not watching plays the animation the first time it is opened. The device remembers which stamps it has played, so the animation runs once; later openings show the stamp at rest. With reduced motion, the stamp is shown at rest.
- The fan can share an image of the ticket's front, which holds no personal details. The image has no stamp, no QR code and no ticket id. It is passed as a file to the device's share sheet, or downloaded where file sharing is missing.
- The image CDN sends `Access-Control-Allow-Origin` with every cover image, so the cover can be drawn into the face and into the share image.
- The front's art is drawn with WebGL (PixiJS) in every browser: the foil follows the ticket's tilt, and the stamp lands with a shockwave and sparks. On Chrome 157 and later the whole ticket, text included, is drawn as a sheet with HTML-in-Canvas while staying real, selectable text, so it bends like paper as it turns over. On Safari and Firefox the text stays ordinary DOM over the art and the ticket turns as a rigid card. Without WebGL the front shows the plain cover image.
- Not in this change: opening the virtual ticket from a dashboard event card (owner's decision: later). The dashboard's event detail sheet stays a popover sheet.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/route/tickets`: adds the virtual ticket with its two sides and designs, the admission stamp and the share image, and extends the supported-browsers requirement to them.

## Impact

- frontend: the tickets route (`tickets-route.ts` / `.html`) gains `openTicket` and starts the stamp from `refreshStates`; a new `virtual-ticket` component, its two renderers and the image export; `IWalletStorage` gains a store of stamped ticket ids (IndexedDB version 2); the chosen designs are kept in `localStorage`. `pixi.js` (pinned to a `dev` build until 8.23 is released) and `pixi-filters` become dependencies, loaded lazily and precached by the service worker; six `@fontsource` display faces are loaded lazily and not precached.
- cloud-provisioning: a CORS response header on the CDN backend bucket of the served bucket (`object-storage.ts`). The production `pulumi up` must run before the frontend adds `crossorigin` to the cover image, or cover images stop loading for every fan.
- backend, proto, the reception app: unchanged. The tickets screen already has every value the face shows (`WalletEventGroup.event`, `WalletTicket`, `WalletPersonalDetails`).
- Follow-up: a separate proposal for opening the virtual ticket from the dashboard.
