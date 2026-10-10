# Tasks

## 1. Access check (cloud-provisioning, read-only)

- [ ] 1.1 Confirm that the `organizer-console-api` service account may read object metadata in the prod internal media bucket (`liverty-music-prod-organizer-media-internal`); verify from the bucket's IAM policy (`gcloud storage buckets get-iam-policy`) and record the role in design.md D1. If it is missing, add the grant to `src/gcp/components/organizer-media.ts` as a task in this group

## 2. Entity operation (components/entity/media/original-exists)

- [ ] 2.1 Declare `OriginalExists` on the image storer interface and implement it on `GCSStorer` (object attributes read; `storage.ErrObjectNotExist` → false); verify contract tests: Uploaded original, Another organizer's upload, Nothing uploaded

## 3. Usecase (components/usecase/media/attach-media)

- [ ] 3.1 In `MediaUseCase.AttachMedia`, check the caller's upload (design D1) before recording, and return Unavailable when publishing `MEDIA.uploaded` fails (design D2); verify unit tests with the operations mocked: Another organizer's media id, Nothing uploaded, Announcement fails, Repeated attach after processing, and the existing Missing media id, Another organizer's series, Cover replaced later, Repeated attach

## 4. Delivery (backend)

- [ ] 4.1 Open the backend PR citing this change, get `make check` and CI green, merge, and cut a release
- [ ] 4.2 In production, upload a cover for a test concert from the organizer console and verify the cover is processed (the CDN `large.webp` answers 200) and the organizer API logs show AttachMedia `status: ok`
