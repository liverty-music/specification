## Why

TicketSBT コントラクトは Base Sepolia にデプロイ済みだが、既存テストは 7 件のみで、approve/setApprovalForAll のブロック検証、3引数 safeTransferFrom、二重 mint、address(0) mint、supportsInterface、ロール管理といった重要な観点が未テスト。mainnet デプロイ前にテストの穴を塞ぎ、静的解析による自動脆弱性検出を CI に組み込む必要がある。

## What Changes

- TicketSBT のテストケースを大幅に追加（approve ブロック、エッジケース、fuzz テスト、supportsInterface、AccessControl ロール管理）
- Foundry fuzz テスト (`testFuzz_` prefix) を導入し、ランダム入力での堅牢性を検証
- Slither 静的解析を CI ワークフローに追加（GitHub Action: `crytic/slither-action`）
- `forge snapshot` によるガスベースライン作成と CI でのガス回帰検出
- approve / setApprovalForAll を override して revert させるかの設計判断と、必要に応じた実装

## Capabilities

### New Capabilities

- `sbt-test-coverage`: TicketSBT コントラクトのテストカバレッジ強化（unit test 追加、fuzz test 導入、エッジケース網羅）
- `sbt-static-analysis`: Slither による Solidity 静的解析の CI 統合とガス回帰検出

### Modified Capabilities

(none)

## Impact

- `backend/contracts/test/TicketSBT.t.sol`: テストケース大幅追加
- `backend/contracts/src/TicketSBT.sol`: approve/setApprovalForAll の override 追加の可能性
- `.github/workflows/test.yml`: Slither ジョブ追加、forge test の fuzz-runs 増加、forge snapshot ステップ追加
- `backend/contracts/.gas-snapshot`: 新規ファイル（git 管理）
