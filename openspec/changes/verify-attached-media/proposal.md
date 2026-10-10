## Why

AttachMedia records any Media id the caller sends and announces it for processing, without checking that the caller's Organizer uploaded it. Media ids appear in public CDN URLs (`media.liverty-music.app/cdn/<organizer>/<media>/large.webp`). Processing reads the original from the folder of the Organizer the Media is recorded for and then makes that Media the cover of the caller's Series (`MediaUseCase.ProcessMedia` → `CutOverSeriesMedia`). So an operator who attaches another Organizer's Media id can make that image their own cover, and replacing their cover later deletes the old Media's row and variants (inferred from the cut-over path, not reproduced). In addition, a failed processing announcement is only logged while AttachMedia succeeds, so the cover is never processed and nothing tells the operator. Found by the organizer console audit of 2026-10-10.

## What Changes

- AttachMedia accepts a Media id only when an uploaded original for that id exists under the caller's Organizer, or when the Media is already recorded for the caller's Organizer (a repeated attach). Otherwise it fails with PermissionDenied when the Media is recorded for another Organizer, and with FailedPrecondition when nothing was uploaded; nothing is recorded or announced.
- A failed processing announcement fails AttachMedia with Unavailable, so the console reports it and the operator retries. A repeated AttachMedia announces again while the original is still waiting to be processed.

## Capabilities

### New Capabilities

- `components/entity/media/original-exists`: tells whether the original uploaded for a Media exists under an Organizer.

### Modified Capabilities

- `components/usecase/media/attach-media`: only the caller's own upload is accepted, and a failed announcement fails the call.

Unchanged, and relied on: `components/entity/media` (no attribute changes), `Media.InsertMedia` and `Media.FindMediaByID` (reading which Organizer a recorded Media belongs to), and `components/usecase/media/create-media-upload-url`, whose upload authorization already places the original under the caller's Organizer.

## Impact

- **backend:** `internal/usecase/media_uc.go` (AttachMedia), a new `OriginalExists` on the image storer (`internal/infrastructure/gcp/storage`), tests. No proto change: the organizer RPC already documents PermissionDenied and FailedPrecondition is a standard code; the console shows its generic save error until `redesign-organizer-console` words it.
- **cloud-provisioning:** none. `organizer-console-api` already reads the internal bucket's objects (it signs uploads into it); confirm it may read object metadata (task 1.1).
