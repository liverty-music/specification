## Context

Phase 1 (sbt-test-hardening) の完了を前提とする。Phase 1 完了時点で、TicketSBT は approve/setApprovalForAll の override、網羅的な unit test、fuzz test、Slither CI、ガス回帰検出を備えた状態になっている。Phase 2 では「テストが十分か」と「全入力で安全か」を証明するレイヤーを追加する。

## Goals / Non-Goals

**Goals:**
- Halmos で「transferFrom/approve は全入力で revert する」「MINTER_ROLE なしでは mint 不可」を数学的に証明する
- Foundry invariant テストで、ランダムなトランザクションシーケンス後も SBT 不変条件が保たれることを検証する
- Aderyn を Slither と併用し、検出パターンの網を広げる
- vertigo-rs で mutation テストを実行し、テストスイートが変異を見逃さないことを確認する
- forge coverage で行/ブランチカバレッジを可視化する

**Non-Goals:**
- Certora Prover の導入（CVL の学習コストが小さいコントラクトに見合わない）
- Echidna / Medusa の導入（Foundry invariant + Halmos で十分）
- mainnet デプロイ（別 change で管理）
- 競争的監査（Sherlock/Code4rena）の実施

## Decisions

### D1: Halmos テストの構造

**選択:** `test/halmos/` ディレクトリに `TicketSBT.halmos.t.sol` として分離。関数名は `check_` prefix（Halmos 規約）。

**理由:** Halmos テストは Foundry の `forge test` では実行されない（`check_` prefix）。分離することで CI ジョブを独立させ、Halmos の遅い実行が通常テストをブロックしない。

**代替案:** 同一ファイルに混在 → 不採用。可読性とCI分離の観点で分離が優れる。

### D2: Invariant テストの Handler パターン

**選択:** `test/invariant/` に Handler コントラクトを配置。Handler が mint のみ呼べるよう制約し、ghost variable で mint 済み tokenId リストを管理。

**理由:** Foundry の invariant テストは Handler 経由でコントラクトを操作する。Handler が現実的な操作に絞ることで、意味のある状態遷移のみ探索する。ghost variable でテスト側の期待値を追跡する。

### D3: Aderyn の CI 統合方式

**選択:** Slither ジョブと並列に `aderyn` ジョブを追加。Aderyn は markdown レポートを出力し、PR コメントとしてアップロード。

**理由:** Slither と異なる AST ベースの解析を行い、補完的な発見が期待できる。Rust 製で高速。

### D4: Mutation テストの実行タイミング

**選択:** CI の weekly スケジュールまたは手動トリガー。PR ごとの自動実行はしない。

**理由:** vertigo-rs はテストスイート全体を変異数 × 実行するため遅い。小さいコントラクトでも数分かかる。PR ごとに実行するとフィードバックループが遅くなる。

## Risks / Trade-offs

- **[Risk] Halmos が OZ の複雑な内部ロジックでタイムアウト** → Mitigation: `--loop-bound` や `--solver-timeout` を調整。OZ の ERC721 は広く使われており Halmos での実績あり。
- **[Risk] vertigo-rs が Foundry の最新版と非互換** → Mitigation: 互換性を事前に確認。問題があれば Gambit + 手動実行にフォールバック。
- **[Risk] Aderyn の false positive が多い** → Mitigation: `.aderyn.toml` で除外設定。初回実行時にトリアージ。
- **[Risk] Phase 1 が未完了のまま Phase 2 に着手** → Mitigation: Phase 2 の tasks は Phase 1 完了を前提条件として明記。
