## Context

See proposal.md. The upload authorization from CreateMediaUploadURL is a signed PUT bound to the object key `<organizer id>/<media id>` in the internal bucket (`GCSStorer.SignedPutURLForOriginal`), so only the Organizer the id was minted for can create that object. Nothing is stored at mint time (spec `usecase/media/create-media-upload-url`).

## Goals / Non-Goals

**Goals:** a Media id reaches processing only for the Organizer that uploaded it; a lost announcement is visible to the operator.

**Non-Goals:** recording media at mint time; changing the processor; a media status read for the console.

## Decisions

### D1 — Ownership is proven by the uploaded object, not by a mint-time record

- AttachMedia checks `Media.OriginalExists(callerOrg, mediaID)` (a metadata read of `<callerOrg>/<mediaID>` in the internal bucket). The object can exist only if the caller's Organizer uploaded it with its own authorization.
- When the original is gone, `Media.FindMediaByID` decides: recorded for the caller → a repeated attach after processing, which succeeds without announcing; recorded for another Organizer → PermissionDenied; not recorded → FailedPrecondition (never uploaded, or the authorization expired unused).
- **Rejected — record the Media at mint time:** a new row per upload authorization, most never attached, and a change to the CreateMediaUploadURL promise ("nothing is stored") for the same guarantee.

### D2 — Announcement failure fails the call

- AttachMedia returns Unavailable when publishing `MEDIA.uploaded` fails. The row insert is idempotent and the original still exists, so the console's retry records nothing new and announces again.
- **Rejected — an outbox:** durable re-announcement for a few uploads a month; the operator's retry is enough.

## Risks / Trade-offs

- [The storer's service account cannot read object metadata in the internal bucket] → task 1.1 checks the IAM binding before the code change; `roles/storage.objectAdmin` on the bucket (the console's grant) includes `storage.objects.get`.
- [A retry after processing already succeeded] → D1 makes it a no-op success.
