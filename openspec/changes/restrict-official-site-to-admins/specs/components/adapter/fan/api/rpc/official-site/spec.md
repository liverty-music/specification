## REMOVED Requirements

### Requirement: Official site calls need a signed-in caller

**Reason**: The fan boundary no longer serves official site calls. Any signed-in fan could set an artist's official site (backend#919); only an admin may.

**Migration**: Admins call `Create` and `Update` of `components/adapter/admin/api/rpc/official-site`. No fan client called the service.

### Requirement: Official site requests are validated at the boundary

**Reason**: The fan boundary no longer serves official site calls.

**Migration**: The same validation applies on `components/adapter/admin/api/rpc/official-site`.

### Requirement: Official sites are created through the boundary but never deleted

**Reason**: The fan boundary no longer serves official site calls, and the reserved Delete had no usecase and no requirement reading it.

**Migration**: Create moves to `components/adapter/admin/api/rpc/official-site`; Delete is not carried over.
