## Context

`UserUseCase.Delete` checks the deletion blockers and removes the identity and the User under the User's deletion lock, a PostgreSQL advisory lock that must be held by a session for as long as the check runs. `UserRepository.SerializeDeletion` held it in a transaction on a pooled connection and ran the rest of the deletion on other connections.

## Decisions

### A Sold listing does not block deletion

The specs list the blockers exhaustively ("Four kinds of blocker") and say that a ResaleListing in any other status does not block. Refunding a Sold listing reads the Order and the payment provider's charge, never the User, so the money reaches the card of a deleted account all the same. The only step that needs the User is the sold email, which has no recipient after the deletion. So the deletion keeps going through, and `SendResaleSold` skips the email when `User.Get` fails with NotFound. A new blocker kind would need a new value in the `DeletionBlockerKind` proto enum and a new line on the withdrawal screen, for a window between the sale and its refund that lasts seconds; it is not taken. Skipping returns success rather than an error: the announcement is delivered once more only on failure, and a User that is gone stays gone.

The poison-queue path was read from the code, not reproduced: `ResaleListingRefundedConsumer.Handle` retries only Unavailable and DeadlineExceeded and returns any other error to the router, which retries and then moves the message to the poison queue.

### One connection for a deletion

`SerializeDeletion` binds the context it passes to `fn` to the lock's transaction, and `TracedPool.Query`, `QueryRow` and `Exec` run on that transaction when the context is bound. The reads and the delete under the lock then use the connection that holds the lock, and the transaction commits when `fn` succeeds. A deletion used two connections at least, and with a pool of one it waited for itself; now it uses one. The lock's semantics are unchanged: creators of blocking records still wait on the shared lock until the commit, and then find the User gone.

Rejected: a lock that holds no connection. An advisory lock lives in a session, and a stored marker needs a schema change for a defect a bound context fixes.
