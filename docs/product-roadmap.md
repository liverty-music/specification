# Ticket Management System Product Roadmap (2026 Edition - Revised)

本ドキュメントは、チケット転売防止システムの詳細な開発ロードマップを定義する。
`ticket-management-system-draft.md` で定義された包括的アーキテクチャを、確実に動作可能な小さなマイルストーンに分解し、開発リスクを最小化する。

> [!IMPORTANT]
> **MVP の定義**: 本ロードマップにおける MVP (Phase 1) は、「KYC なしでチケット購入・SBT発行までのフロー」が動作する状態を指す。ZKP 入場は Phase 1.5 に分割し、MVP のスコープを意図的に縮小している。

---

## Roadmap Overview

```
Phase 1     Phase 1.5     Phase 2     Phase 2.5   Phase 3     Phase 4
└──────────┴─────────────┴───────────┴───────────┴───────────┴───────────▶
  MVP         Entry        Mock KYC    Real KYC    Resale      Production
(Purchase)   (ZKP)        (VC Stub)   (OID4VCI)   (Escrow)    (Mobile)
```

| Phase | Name | Focus | Deliverables |
| :--- | :--- | :--- | :--- |
| **1** | **MVP: Purchase Flow** | Core UX | Passkey Auth, SBT Minting, **PWA Foundation** |
| **1.5** | **Entry Flow** | Privacy | ZKP (WASM), **Offline Support**, Service Worker Cache |
| **2** | **Mock KYC** | Compliance Prep | Manual VC Issuance, Purchase Gate (VC Check) |
| **2.5** | **Real KYC** | Compliance | OID4VCI Integration, eKYC Vendor API |
| **3** | **Authorized Resale** | Liquidity | Burn/Mint Flow, Escrow Contract, Price Enforcement |
| **4** | **Production & Optimization** | Scale | **Advanced PWA Features**, Mainnet Launch |

---

## Phase 1: MVP - Purchase Flow (KYC-less)

**User Story**
- _"As a User, I want to create an account with FaceID (Passkey) and purchase a ticket without managing seed phrases, so that I can easily access web3 ticketing."_
- _"As an Issuer, I want to mint SBTs to specific user accounts and have the gas fee paid by the system, so that users don't need to hold crypto."_

**Goal**
シードフレーズ不要の「Web2ライクな購入体験」で、SBT発行までが動作する最小構成を構築する。入場認証（ZKP）は次フェーズに移譲し、MVPスコープを縮小する。

### 1.1 Functional Requirements
1.  **Authentication (Passkey & Smart Accounts)**
    -   WebAuthn でFIDO2 Passkey (P256) を作成。
    -   ERC-4337 Smart Account をユーザーごとにデプロイ (または Counterfactual Address)。
    -   RIP-7212 対応チェーン (Base Sepolia) を選定。
2.  **Ticket Management (SBT)**
    -   `TicketSBT.sol`: ERC-721 + ERC-5192 (OpenZeppelin v5)。
    -   `mint(address to, uint256 tokenId)`: Issuer (Owner) のみ実行可能。
    -   `_update` フックで転送を禁止。
    -   Semaphore Identity Commitment (将来の ZKP 用) の登録はこの段階ではオプション。
3.  **Gasless Experience (Paymaster)**
    -   Go バックエンドに `Verifying Paymaster` を実装。
    -   ポリシー: `mintTicket` 等の許可リスト関数のみをスポンサー対象とする。
    -   Rate Limit (RLN) によるスパム防止。
4.  **PWA Foundation (Aurelia 2)**
    -   **App Shell**: Aurelia 2 で SPA を構築。
    -   **Manifest**: ホーム画面追加 (A2HS) をサポートし、ネイティブアプリライクな起動を実現。
    -   **Service Worker**: 基本的な静的アセットのキャッシュ。

### 1.2 Data Model (PostgreSQL)
| Table | Purpose | Columns (Example) |
|---|---|---|
| `users` | ユーザーと Smart Account のマッピング | `passkey_credential_id`, `smart_account_address`, `created_at` |
| `events` | イベントマスタ | `event_id`, `name`, `date`, `venue`, `ticket_contract_address` |
| `tickets` | 発行済みチケットメタデータ | `token_id`, `event_id`, `seat`, `owner_address`, `status` |

### 1.3 Technical Stack
-   **Backend**: Go (**Connect RPC**), PostgreSQL
-   **Frontend**: Aurelia 2 (PWA), `viem`, `permissionless.js`, `simplewebauthn`
-   **Chain**: Base Sepolia
-   **Infra**: **GKE**, Cloud SQL, Pimlico (Bundler)

### 1.4 Challenges & Mitigations
| Challenge | Mitigation |
|---|---|
| P256 ガス代高騰 (RIP-7212 非対応チェーンの場合) | RIP-7212 対応 L2 (Base, OP) を選定 |
| Passkey の Cross-Device Sync | Passkey の Discoverable Credential 特性を利用 / Recovery Key の検討 |
| Smart Account デプロイコスト | Counterfactual Address を利用し初回トランザクション時にデプロイ |

### 1.5 Deliverables
-   [ ] `TicketSBT.sol` デプロイ (Testnet)
-   [ ] Go Backend: Passkey Auth, Paymaster サービス稼働
-   [ ] Frontend: Passkey 登録 → 購入（モック決済） → SBT確認フロー動作確認
-   [ ] **PWA**: PWA Audit (Lighthouse) Pass, Installable on iOS/Android
-   [ ] **Demo Video**: 購入フローのE2Eデモ (PWA Standalone Mode)

---

## Phase 1.5: Entry Flow (ZK Proof)

**User Story**
- _"As a User, I want to generate a QR code on my phone that proves I own a ticket without revealing my identity, so that I can enter the venue privately."_
- _"As a Verifier, I want to scan a QR code and instantly know if it's valid and unused, so that I can manage entry efficiently."_

**Goal**
ZKP によるプライバシー保護入場を実現する。「SBT を持っている」ことを「匿名で」「一度だけ」証明できる。

### 1.5.1 Functional Requirements
1.  **Semaphore Identity**
    -   購入時にブラウザで `Identity` を生成、LocalStorage (または IndexedDB) に保存。
    -   `IdentityCommitment` を Go Backend 経由でオンチェーン Merkle Tree に登録。
2.  **Proof Generation (Client-Side & Offline)**
    -   Aurelia アプリで `snarkjs` (WASM) を用いて Groth16 Proof を生成。
    -   **Service Worker Cache**: 巨大な回路ファイル (`.zkey`, `.wasm`) をキャッシュし、**完全オフライン**での証明生成を実現する。
    -   **Web Worker**: 計算処理をバックグラウンドスレッドに逃がし、UIフリーズを防ぐ。
3.  **Verification**
    -   **On-chain**: `TicketSBT` または別途 `Verifier.sol` で Groth16 検証。
    -   **Off-chain (Recommended for MVP)**: Go Backend で `rapidsnark` / `gnark` による高速検証。NullifierHash を Redis に記録。

### 1.5.2 ZK Circuit (Circom)
-   `TicketCheck.circom`:
    -   Inputs: `identityNullifier`, `identityTrapdoor`, `treeSiblings[N]`, `treePathIndices[N]`, `externalNullifier`, `root`
    -   Outputs: `nullifierHash`
-   **Trusted Setup**: Powers of Tau (Community Ceremony) または プロジェクト固有 Ceremony の実施。

### 1.5.3 Data Model Additions
| Table | Purpose | Columns (Example) |
|---|---|---|
| `merkle_tree` | Commitment と Merkle Path の管理 | `leaf_index`, `commitment_hash`, `path_elements`, `path_indices` |
| `nullifiers` | 使用済み Nullifier の記録 (二重入場防止) | `nullifier_hash`, `event_id`, `used_at` |

### 1.5.4 Challenges & Mitigations
| Challenge | Mitigation |
|---|---|
| ブラウザ WASM での証明生成速度 | `snarkjs` の Worker 利用、回路サイズ削減 (Merkle Depth 最適化) |
| Trusted Setup | Semaphore 公式の既存 Setup を利用 (回路カスタマイズ不要の場合)、またはプロジェクト固有 Ceremony 実施 |
| Merkle Tree の同期 | オンチェーン Root とオフチェーンキャッシュの一貫性担保 (Event Listener) |

### 1.5.5 Deliverables
-   [ ] Circom 回路コンパイル & Trusted Setup 完了
-   [ ] Frontend: QR コード生成 UI
-   [ ] Backend: Verifier エンドポイント (Proof 検証 → Nullifier 記録)
-   [ ] **Integration Test**: 購入 → 入場 フローの E2E テスト

---

## Phase 2: Mock KYC (VC Stub)

**User Story**
- _"As a User, I want to upload a selfie and ID for verification, then receive a badge (VC) that lets me buy premium tickets."_
- _"As an Issuer, I want to gate certain tickets to verified users only."_

**Goal**
外部 eKYC ベンダーとの連携**前に**、VC 発行・VC チェックのフローを構築する。裏側は手動承認またはスタブ。

### 2.1 Functional Requirements
1.  **Mock KYC Flow**
    -   UI: Self-Photo and ID Document upload form.
    -   Backend: 管理者手動承認 (Admin Dashboard) or Auto-Approve (Stub).
2.  **VC Issuance (Stub)**
    -   `VerifiedFanCredential` を Go Backend 秘密鍵で署名し、ユーザーへ返却。
    -   VC フォーマット: SD-JWT (Selective Disclosure)。
3.  **Purchase Gate**
    -   チケット購入 API で VC 保有 (Presentation) を検証。

### 2.2 Deliverables
-   [ ] KYC Stub UI (Upload form)
-   [ ] Admin Dashboard (Review & Approve)
-   [ ] VC Issuance endpoint
-   [ ] Purchase API の VC Presentation 検証ロジック

---

## Phase 2.5: Real KYC (OID4VCI Integration)

**User Story**
- _"As a User, my verification experience is seamless and I receive my VC automatically after eKYC approval from a real provider."_

**Goal**
外部 eKYC ベンダー (例: Liquid, Minna-no-eKYC) と連携し、標準規格 OID4VCI で VC を発行する。

### 2.5.1 Functional Requirements
1.  **eKYC Integration**
    -   ベンダー API との OAuth2/OpenID Connect 連携。
    -   Webhook 受信 → VC 発行トリガー。
2.  **OID4VCI Issuer**
    -   Credential Offer Endpoint
    -   Token Endpoint (PAR/DPoP)
    -   Credential Endpoint

### 2.5.2 Technical Challenges
-   OID4VCI 標準規格の複雑さ (`trustbloc/wallet-sdk` 等のライブラリ活用で緩和)
-   eKYC ベンダーとの契約・SLA

### 2.5.3 Deliverables
-   [ ] eKYC Provider Integration (Sandbox / Staging)
-   [ ] OID4VCI Issuer Implementation (Go)
-   [ ] VC Wallet Integration (Frontend SDK)

---

## Phase 3: Authorized Resale (Marketplace)

**User Story**
- _"As a User (Seller), I want to return my ticket for a face-value refund if I can't attend."_
- _"As a User (Buyer), I want to buy a returned ticket at face value from the official pool."_

**Goal**
SBT の「Burn & Re-Mint」による興行主公認リセールを実現する。定価強制により不正転売を根絶。

### 3.1 Functional Requirements
1.  **Resale Request Flow**
    -   Seller: アプリから「リセール申請」→ Smart Contract `submitResale(tokenId)`
    -   Backend: SBT burn & Ticket status → `Available for Resale`
2.  **Repurchase Flow**
    -   New Buyer: Face Value で購入 → Backend: Mint to new owner
3.  **Escrow Contract**
    -   `TicketEscrow.sol`:
        -   Seller への返金と手数料徴収を自動処理。
        -   法的リスク検討: 収納代行との線引き (資金決済法との関係を法務確認)。

### 3.2 Legal & Compliance Consideration
> [!CAUTION]
> 日本法下での「収納代行」扱いの有無について法務確認が必須。代金が興行主のウォレットを経由する設計とすることで、スマートコントラクトがユーザー資金を預かる形を回避する設計を推奨。

### 3.3 Deliverables
-   [ ] `TicketEscrow.sol` (Testnet deploy)
-   [ ] Resale UI (Seller / Buyer)
-   [ ] 法務レビュー完了

---

## Phase 4: Production & PWA Optimization

**User Story**
- _"As a User, I receive push notifications for my upcoming events and can access my tickets instantly even with unstable network."_

**Goal**
ドームクラス数万人規模のスケーラビリティと、PWAとしての完成度を極める。

### 4.1 Functional Requirements
1.  **Advanced PWA Features**
    -   **Web Push Notifications**: イベントリマインダー通知 (iOS 16.4+ / Android)。
    -   **Background Sync**: オフライン時に行われたアクションの再同期。
    -   **Persistent Storage**: ブラウザストレージの永続化要求。
2.  **Mainnet Launch**
    -   Base Mainnet or Optimism Mainnet deployment.
    -   Security Audit (Smart Contracts + Backend).
3.  **Scalability**
    -   Go Backend: Redis Caching, Connection Pooling.
    -   DB: Read Replica / Sharding Strategy.
    -   Self-hosted Bundler Node (Backup).

### 4.2 Deliverables
-   [ ] Web Push Notification Implementation
-   [ ] Security Audit Report (Smart Contract)
-   [ ] Mainnet Deployment Runbook
-   [ ] Monitoring & Alerting (Observability Stack)

---

## Phase 4+ (Post-Launch): Advanced Features

| Feature | Description | Priority |
|---|---|---|
| **zkVM (SP1/RISC Zero)** | Rust で複雑な証明ロジックを記述可能に (例: Fan Club Tier Check) | Medium |
| **EIP-7702 Support** | 既存 EOA ユーザーへのハイブリッドオンボーディング | Low (Niche) |
| **Delegated Proving Server** | 低スペック端末向けに Proof 生成を委任 | Low (UX improvement) |

---

## Appendix A: Systems Component Impact Per Phase

| Component | Phase 1 | Phase 1.5 | Phase 2 | Phase 2.5 | Phase 3 | Phase 4 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Go Backend** | Auth, Paymaster | - | KYC Stub | OID4VCI | Resale API | Scaling |
| **Smart Contract** | ERC-5192 | Semaphore Verifier | - | - | Escrow | Mainnet |
| **Frontend** | Aurelia PWA(Basic) | Offline ZKP (SW) | VC UI | - | Resale UI | Web Push |
| **Database** | users, events, tickets | merkle_tree, nullifiers | kyc_status | vc_metadata | escrow_txs | Replica |

---

## Appendix B: Database Schema (Reference)

```sql
-- Phase 1
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passkey_credential_id TEXT UNIQUE NOT NULL,
    smart_account_address TEXT UNIQUE NOT NULL, -- 0x...
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE events (
    event_id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    date DATE NOT NULL,
    venue TEXT,
    ticket_contract_address TEXT NOT NULL
);

CREATE TABLE tickets (
    token_id INTEGER NOT NULL,
    event_id UUID REFERENCES events(event_id),
    seat_info JSONB,
    owner_address TEXT NOT NULL,
    status TEXT CHECK (status IN ('active', 'burned', 'resale_pending')),
    PRIMARY KEY (token_id, event_id)
);

-- Phase 1.5
CREATE TABLE merkle_tree (
    leaf_index SERIAL PRIMARY KEY,
    event_id UUID REFERENCES events(event_id),
    commitment_hash TEXT UNIQUE NOT NULL, -- Poseidon hash
    path_elements TEXT[] -- For client proof generation hint (optional cache)
);

CREATE TABLE nullifiers (
    nullifier_hash TEXT PRIMARY KEY,
    event_id UUID REFERENCES events(event_id),
    used_at TIMESTAMPTZ DEFAULT NOW()
);

-- Phase 2
CREATE TABLE kyc_requests (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    status TEXT CHECK (status IN ('pending', 'approved', 'rejected')),
    reviewed_at TIMESTAMPTZ
);
```
