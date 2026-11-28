## Context

The fan `OfficialSiteService` is registered in `fanHandlers` of `internal/di/api_wiring.go` and does no role check, so every signed-in fan reaches `OfficialSiteUseCase.Create`. The admin server gates every service registered in `adminHandlers` on the admin role (see `components/adapter/admin/api/rpc/artist`), so moving the service there is what restricts it. `Artist.UpdateOfficialSiteURL` already exists for the daily refresh; nothing exposes it to a person.

## Goals / Non-Goals

**Goals:**
- Only an admin can create an artist's official site, and an admin can replace a wrong URL.

**Non-Goals:**
- Deleting an official site, or stopping the daily refresh from replacing a corrected URL (see Risks).
- An admin console screen for official sites, and an admin read of an artist's current official site. Until a console change adds them, staff call `Create` and `Update` directly on the admin server with an admin sign-in, and read the current URL from the database.

## Decisions

### D1. A new admin package, and the fan package is removed

The rpc-design rules name the caller in the package (`rpc.admin.`), so a role check inside the fan package would put an admin call in a fan package. The new package is `liverty_music.rpc.admin.official_site.v1` with the service name `OfficialSiteService` (the entity's name). The fan package is removed instead of kept: its only caller would be a fan who must not call it. A removal breaks generated clients, but none exists (`grep` of the frontend and cloud-provisioning finds no reference).

Alternative: keep the fan service and add a role check in the handler. Rejected: the boundary of a fan call then refuses fans, and the next reader cannot tell the rule from the package name.

### D2. Update takes the artist id and the URL

An artist has at most one official site, and `Artist.UpdateOfficialSiteURL` is keyed by the artist id, so `Update` takes `artist_id` and `url` instead of an official site id the caller would have to look up first. `OfficialSiteUseCase.Update(ctx, artistID, url)` returns the error of `Artist.UpdateOfficialSiteURL` unchanged.

Alternative: `SetUrl` as a `Set<Attribute>` call. Rejected: `Update` replaces the resource's mutable fields, and the URL is the only one.

### D3. `Delete` is dropped

The reserved `Delete` failed with Unimplemented for every caller and no requirement reads it. A deletion can be added with its first requirement.

### D4. No locking

`Create` relies on the unique artist constraint and `Update` is one statement on one row; neither checks a condition and then acts across rows.

## Risks / Trade-offs

- [The daily official site refresh replaces the stored URL whenever the music catalog resolves to a different one (`components/usecase/artist/refresh-official-site`), so an admin's correction lasts only until the next check of that artist, at most 7 days, when the catalog disagrees] → An admin's correction still holds while the catalog has no homepage for the artist, and it is what the next search reads in the meantime. Keeping a correction against the catalog needs a decision (a flag on the site, or a catalog that is trusted less), which this change leaves to the owner; it is reported in the pull request.
- [Removing the fan package breaks a client built against it] → There is none; the removal PR carries the `buf skip breaking` label.

## Migration Plan

1. Merge the proto PR and cut the Release; wait for BSR generation.
2. Merge the backend PR (the admin handler, the wiring change and the usecase), then release it.
3. Verify read-only in prod: the rollout finished and no `official_site.v1.OfficialSiteService` request is served by fan-api.
