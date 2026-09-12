## 0. Verify current state (do first)

- [ ] 0.1 Read ④'s shipped backend capture path (backend #426) — is it a destination
      charge + `on_behalf_of`, an already-separate charge, or stubbed pending Stripe
      KYC? This scopes everything below.
- [ ] 0.2 Confirm no proto/entity field encodes the destination-charge assumption
      (`Order`/`Payment` should stay provider-agnostic — no schema change expected).

## 1. Spec (specification)

- [ ] 1.1 MODIFIED `lottery-application` "Capture winners and release losers at the
      draw": capture = platform-held separate charge (funds on platform balance, no
      destination/on_behalf_of at capture), Organizer settlement via post-event
      Transfer. (Delta written; validate --strict; merge PR → Release if it bumps a
      version — spec-only, no BSR types.)

## 2. Backend — capture topology (lottery-application)

- [ ] 2.1 Change the draw-capture to a **separate charge** on the platform: drop
      `transfer_data[destination]` / `on_behalf_of`; platform is settlement merchant;
      funds land on the platform balance.
- [ ] 2.2 Keep the fee as the retained portion (platform take = amount − Organizer
      net); loser release (cancel authorization) unchanged; JPY/Amex rule unchanged.
- [ ] 2.3 Ensure the ④→⑤ handoff still passes the captured charge id (`source_
      transaction` for ⑤'s Transfer) — no behavior change to the contract.

## 3. Settlement boundary (coordinate with ⑤)

- [ ] 3.1 Confirm the **post-event `Transfer`** is owned by ⑤'s payout controller,
      NOT re-implemented in ④ (④ ends at platform-held capture + handoff). Document
      the boundary in both changes.
- [ ] 3.2 Refund/`transfer_reversal` + reserve draw on the platform balance; platform
      is loss-liable for connected-account negative balances
      (`controller[losses][payments]=application` / Custom-equivalent).

## 4. Stripe Connect configuration

- [ ] 4.1 Platform statement descriptor: Latin static **prefix** (2–10, alphabetic) +
      **kanji/kana** prefixes; per-event `statement_descriptor_suffix` (+ `_kanji`/
      `_kana`) with abbreviated event/organizer name. Respect budgets (Latin 22 total,
      kanji 17, kana 22; no `< > \ ' " *`). Make the **default** descriptor
      recognizable (JCB/Diners/Discover show it during the pre-capture delay).
- [ ] 4.2 Platform account = loss-liable controller config (negative-balance
      responsibility) — also the prerequisite for `allocated_funds` later.

## 5. Stripe-contact items (not answerable from docs — track, don't block MVP)

- [ ] 5.1 Ask the Stripe account manager whether/when **`allocated_funds` (funds
      segregation) will be available for JP** (Japan is NOT in the current eligible
      markets: BE/CH/DE/DK/ES/FR/GB/NL/SE/US; private preview, no published timeline).
- [ ] 5.2 Confirm **single manual-capture is supported under `allocated_funds`** (docs
      imply yes — allocation at capture; only multicapture/overcapture/incremental-auth
      excluded) when requesting preview access.
- [ ] 5.3 Decision: adopt `allocated_funds` for held-fund isolation **only if** JP
      access is granted; otherwise MVP stays on plain separate charges & transfers
      (funds in the general platform balance until Transfer — the JP-incumbent norm).

## 6. Verification

- [ ] 6.1 Stripe test-mode: authorize at apply → capture winner → **funds on the
      PLATFORM balance** (not the connected account) → post-event Transfer to the
      Organizer; loser release; descriptor shows platform prefix + event suffix.
- [ ] 6.2 Sync the delta to the main `lottery-application` spec and archive.
