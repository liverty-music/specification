## Why

SetCoverImage records any SeriesImage id the caller sends and announces it for processing, without checking that the caller's Organizer uploaded it. SeriesImage ids appear in public CDN URLs (`media.liverty-music.app/cdn/<organizer>/<series image id>/large.webp`). Processing reads the original from the folder of the Organizer the SeriesImage is recorded for and then makes that SeriesImage the cover of the caller's Series (`SeriesImageUseCase.Process` → `SeriesImage.ReplaceCover`). So an operator who attaches another Organizer's SeriesImage id can make that image their own cover, and replacing their cover later deletes the old SeriesImage's row and variants (inferred from the cut-over path, not reproduced). In addition, a failed processing announcement is only logged while SetCoverImage succeeds, so the cover is never processed and nothing tells the operator. Found by the organizer console audit of 2026-10-10.

## What Changes

- SetCoverImage accepts a SeriesImage id only when an uploaded original for that id exists under the caller's Organizer, or when the SeriesImage is already recorded for the caller's Organizer (a repeated attach). Otherwise it fails with PermissionDenied when the SeriesImage is recorded for another Organizer, and with FailedPrecondition when nothing was uploaded; nothing is recorded or announced.
- A failed processing announcement fails SetCoverImage with Unavailable, so the console reports it and the operator retries. A repeated SetCoverImage announces again while the original is still waiting to be processed.

## Capabilities

### New Capabilities

- `components/entity/series-image/original-exists`: tells whether the original uploaded for a SeriesImage exists under an Organizer.

### Modified Capabilities

- `components/usecase/series/set-cover-image`: only the caller's own upload is accepted, and a failed announcement fails the call.

Unchanged, and relied on: `components/entity/series-image` (no attribute changes), `SeriesImage.Create` and `SeriesImage.Get` (reading which Organizer a recorded SeriesImage belongs to), and `components/usecase/series-image/create-upload-url`, whose upload authorization already places the original under the caller's Organizer.

## Impact

- **backend:** the SetCoverImage usecase, a new `OriginalExists` on the image storer (`internal/infrastructure/gcp/storage`), tests. No proto change: the organizer RPC already documents PermissionDenied and FailedPrecondition is a standard code; the console shows its generic save error until `redesign-organizer-console` words it.
- **cloud-provisioning:** none. `organizer-console-api` already reads the internal bucket's objects (it signs uploads into it); confirm it may read object metadata (task 1.1).
