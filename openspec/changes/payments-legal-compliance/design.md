## Context

See proposal.md — Why. Paid ticketing (⑤) is implemented and verified in Stripe test mode; livemode is gated by JP legal/tax/compliance obligations. These obligations are cross-cutting: the consumer disclosures (総額表示, 特商法 最終確認) render on UI owned by ④ (`lottery-application` apply/checkout) and ⑤ (`ticket-purchase-and-issuance` Order views); the escrow/payout execution is `ticket-settlement-and-payout`; the legal opinions and tax registration are external actions. No proto/RPC surface changes.

## Goals / Non-Goals

**Goals:**
- One auditable home for the livemode launch gate, decoupled from ⑤'s implementation so ⑤ can archive.
- Express each obligation as an enforceable/observable contract (see spec.md), not a vague checklist.

**Non-Goals:**
- Stripe Connect onboarding / escrow / payout execution (owned by `ticket-settlement-and-payout`).
- Building the checkout/apply UI itself — this capability owns the *obligation*; ④/⑤ own the pixels that satisfy it.
- Flipping to livemode in this change; that is the gated event this capability guards.

## Decisions

- **Separate capability, not ⑤ tasks.** The moved items are launch gates, not ⑤ spec requirements; keeping them in ⑤ would block ⑤'s archive indefinitely on external legal. Alternative (leave in ⑤) rejected for exactly that coupling.
- **Provider decided: Stripe Connect, test mode now.** Live launch deferred behind this gate. No KOMOJU PoC (already settled in ⑤). This keeps PCI scope at SAQ A (Stripe Elements) and frames the 越境移転 disclosure around Stripe (US).
- **媒介者交付特例 stance is a required decision, not assumed.** Whether the platform issues qualified invoices on behalf of Organizers (媒介者交付特例) vs. each Organizer self-issues determines the receipt content (登録番号 placement) and the registration task. Flagged as an open counsel/tax decision in tasks §1.
- **Compliance UI lands in the owning surfaces.** 総額表示 and 特商法 最終確認画面 are implemented in ④/⑤ where the prices/flow already render; this capability specifies the contract and tracks completion, avoiding a duplicate UI layer.

## Risks / Trade-offs

- **External timelines dominate.** Counsel opinion (#778), 税務署 registration, Stripe live 審査, and DPA execution are not engineering-paced; the gate may sit open for a while. Accepted — that is the point of isolating it from ⑤.
- **Split ownership of consumer UI.** The obligation lives here but the pixels live in ④/⑤; risk of drift if a price/flow changes without re-checking 総額表示 / 特商法. Mitigation: the spec scenarios are the cross-surface acceptance check.
- **媒介者交付特例 undecided ⇒ receipt work partially blocked.** The receipt/invoice task cannot finalize content until the stance is chosen; sequence the counsel/tax decision first.
