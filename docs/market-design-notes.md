# Market & Competitor Design Notes (JP ticketing, 2025-2026)

Durable record of the competitor / market research behind the Phase 3
ticketing roadmap, so the design rationale and the two roadmap calibrations
below are not lost. Sources: LivePocket, tiget, ZAIKO, teket (DNP),
チケプラ, ぴあ/e+, チケミー; デジタル庁 マイナンバー実証 2025;
チケトレ shutdown 2025-06; LINEチケット exit 2022.

## Verdict

Our direction **aligns strongly** with where the JP market is heading, and
our sharpest differentiator — **proactive fan auto-notification/discovery** —
is a **white space** among the "後発" (later-generation) pure-plays
(teket / ZAIKO / Peatix don't do it; only legacy ぴあ does a weaker version).
Two calibrations are warranted (below). Web2 (no blockchain) is validated —
NFT ticketing retreated to a theater niche (チケミー); the mainstream is
Web2 + face-auth.

## Dominant 後発 patterns (adopt)

- Zero-fixed-cost, revenue-share-only; **buyer-shiftable flat %** fee (a flat
  % reads cleaner than tiget's stacked ¥220+¥99, which draws complaints).
- **Organizer self-serve is table-stakes** (teket/ZAIKO), not a
  differentiator. (We deliberately chose **vetted partners** for MVP — a
  conscious divergence; our moat is fan-notification + curation, and
  self-serve can open later.)
- **In-platform official face-value resale** is now the market default
  (after the industry チケトレ shut down 2025-06 and resale moved inside
  チケプラTrade / e+ / ぴあ).
- Companion **分配URL (organizer-toggle, returnable)** is standard; plus
  multi-ticket single-buyer group entry (teket/スマチケ).
- Rotating QR + server-side one-time validation is **baseline** (not novel).

## Trend: identity at entry (the moving competitive bar)

- **Hardware-free, on-device face-auth entry** shipped (チケプラ, 2025-12) —
  removes the operator-tablet barrier and is becoming the anti-scalp bar for
  high-demand tours. Photo-bound tickets are now the floor at the leaders.
- **マイナンバーカード linkage** (デジタル庁 2025 実証): zero fraud on linked
  tickets, but low linkage (13-28%) + install friction → treat as an
  **opt-in high-assurance tier**, not mandatory.

## Roadmap calibrations (folded into ticketing-platform-roadmap.md)

- **#2 Pull `official-resale` earlier.** It is both the cannot-attend valve
  and now a market default. Promote from deep Phase 2 to **immediately after
  the lottery/ticketing MVP** (tie it to the lottery loser pool).
- **#3 Add a face-auth anti-scalp tier.** Our ⑥ rotating-QR + Passkey is the
  floor; add **photo-bound → live-face-match-to-open** as a Phase-2 tier, and
  **マイナンバー** as an opt-in high-assurance option. Without it we look a
  generation behind the leaders.

## Watch (not yet calibrations)

- **#4 分配 reconsideration:** the market norm is organizer-toggle,
  returnable, name-bound 分配URL. Our "same-time entry only, no distribution
  URL" is more restrictive; with name-binding/face-auth a returnable,
  account-bound 分配 is scalp-safe and more convenient. Revisit at ⑥.
- **#1 vetted-only vs zero-gate self-serve:** conscious divergence; keep for
  MVP, keep open-self-serve as a future option.
- **#5 fee model:** flat %, buyer-shiftable → see `payments-design.md`.

## The moat, in one line

No 後発 competitor bundles **fan auto-notification × lottery × in-platform
official resale × hardware-free face-auth** in one app. Our existing
fan-notification product is that core.
