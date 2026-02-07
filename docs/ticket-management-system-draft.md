# **次世代チケット転売防止システムの包括的技術アーキテクチャ：SBT、DID、VC、ERC-4337、ZKPの統合（2026年版）**

## **1. エグゼクティブサマリー**

日本のイベント・チケット産業は、長年にわたり不正転売（スキャルピング）、詐欺、そして二次流通市場の制御不能といった課題に直面してきた。これに対し、「特定興行入場券の不正転売の禁止等による興行入場券の適正な流通の確保に関する法律」（チケット不正転売禁止法）が施行され、法的な規制枠組みは整備されたものの、技術的な実装は依然として「イタチごっこ」の様相を呈している。2026年現在、Web3技術の成熟と標準化により、これらの課題を根本から解決する技術的基盤が整った。

本レポートは、Soulbound Tokens (SBT)、Decentralized Identifiers (DID)、Verifiable Credentials (VC)、ERC-4337 Account Abstraction（アカウント抽象化）、およびZero-Knowledge Proofs (ZKP: ゼロ知識証明) を統合した、次世代のチケット転売防止システムの技術的実装に関する網羅的な解説書である。本システムアーキテクチャは、**TypeScript**によるフロントエンド（viem、permissionless.js）、**Go言語**によるバックエンド（OID4VCI標準に基づくVC発行）、および**Solidity**（OpenZeppelin v5）によるスマートコントラクトによって構成される。

提案するアーキテクチャの核心は、チケット（資産）とアイデンティティ（本人確認）をプロトコルレベルで分離しつつ、暗号学的に強固に紐付ける点にある。SBTによりチケットの無断譲渡をブロックチェーン上で物理的に阻止し、VCとDIDにより法的要件である「本人特定」をプライバシーを侵害することなく実現する。さらに、ERC-4337とPasskeyの統合により、ユーザーは秘密鍵の管理から解放され、生体認証によるシームレスな体験を享受できる。そしてZKPは、入場時の「監視社会化」を防ぎつつ、数学的な確実性を持ってチケットの正当な所有権を証明する。

## **2. 規制環境とコンプライアンス要件（2026年の日本市場）**

### **2.1 チケット不正転売禁止法と技術的要請**

日本における適法なチケットシステムを構築するための第一歩は、チケット不正転売禁止法の厳格な遵守である。2026年時点において、デジタルチケットの譲渡に関する規制当局の解釈はより明確化しており、システムには以下の要件が求められる。

* **特定興行入場券の定義**: 第2条第3項に基づき、興行主が販売時に有償譲渡を禁止する旨を明示し、かつ入場資格者の氏名及び連絡先を確認する措置が講じられているチケットが対象となる。
* **本人確認措置のデジタル実装**: 法は、入場資格者（購入者）と入場者が同一であることを求めている。従来のアナログな本人確認（身分証の目視確認）は運用コストが高く、かつ偽造リスクがあるため、2026年のシステムでは、これをデジタル署名と暗号証明によって自動化することが必須となる。具体的には、チケットデータ（SBT）と本人確認データ（VC）が、同一の「所有者（Controller）」に紐付いていることを数学的に保証する必要がある。
* **「転売」の定義と許可された流通**: 法は「業として行う高額転売」を禁止しているが、定価での譲渡（リセール）までを否定しているわけではない。したがって、システムは「プロトコルレベルでの譲渡禁止（SBT）」を基本としつつ、興行主が認めた公式な二次流通（リセール）機能（スマートコントラクトによる定価取引の強制）を実装しなければならない。

### **2.2 プライバシー保護法とデータ最小化原則**

「個人情報の保護に関する法律」（APPI）との整合性も重大な課題である。不正転売を防ぐためにブロックチェーン上にユーザーの実名や電話番号を記録することは、重大なプライバシー侵害であり、コンプライアンス違反となる。

本アーキテクチャでは、**Zero-Knowledge Proofs (ZKP)** と **Verifiable Credentials (VC)** を採用することで、このジレンマを解決する。システムは「ユーザーが実在する人間であり、興行主の規定する本人確認（KYC）を通過した」という事実（述語）のみをオンチェーンまたは検証機に伝達し、氏名や住所などの生データ（属性値）はユーザーのデバイス（Wallet）内に留める「データ最小化」のアプローチを採用する。

### **2.3 2026年の技術動向と市場標準**

2025年から2026年にかけて、チケット技術は「閉域型アプリ」から「相互運用可能なプロトコル」へとシフトしている。TicketmasterのSafeTixのような回転式バーコード技術はスクリーンショット防止には有効だが、中央集権的なサーバーへの依存が残る。Web3アプローチの標準は、**クライアントサイド・プルービング（Client-Side Proving）** である。これは、ユーザーのスマートフォン上でZKPを生成し、サーバーには証明（Proof）のみを送信する方式であり、サーバーがハッキングされてもユーザーの秘密鍵や個人情報が漏洩しない構造を実現する。

## **3. システムアーキテクチャ概要**

本システムは、大きく分けて**ユーザー層（Client）**、**サービス層（Backend）**、**オンチェーン層（Blockchain）**の3層構造で構成される。各層は疎結合でありながら、暗号学的証明によって信頼の連鎖（Chain of Trust）を形成する。

| レイヤー | コンポーネント | 技術スタック (2026標準) | 役割と機能 |
| :---- | :---- | :---- | :---- |
| **Frontend** | ユーザーウォレット / アプリ | **TypeScript** (React Native / Next.js) | UI、Passkey生成、ZKP生成、DID管理 |
| | Web3インタラクション | viem, permissionless.js | ERC-4337 UserOperationの構築、署名 |
| | アイデンティティSDK | trustbloc/wallet-sdk-typescript | VCの受信、保存、提示（OID4VCI/VP） |
| **Backend** | API ゲートウェイ | **Go** (Golang 1.25+) | REST/gRPCエンドポイント、セッション管理 |
| | VC発行サービス (Issuer) | Go (trustbloc/wallet-sdk) | OID4VCI実装、KYCデータとの照合、VC署名 |
| | ZK検証サービス (Verifier) | Go (gnark or rapidsnark wrapper) | オフチェーンでのZKP高速検証、Nullifier管理等 |
| | データベース | PostgreSQL, Redis | オフチェーンメタデータ、Nonce、イベント情報の管理 |
| **Blockchain** | チケットコントラクト | **Solidity** (OpenZeppelin v5) | ERC-721 + ERC-5192 (SBT)、所有権管理 |
| | アカウントコントラクト | Solidity (ERC-4337 / EIP-7702) | Smart Accounts (Safe/Kernel)、WebAuthn検証 |
| | 検証コントラクト | Solidity (Groth16 Verifier/SP1) | オンチェーンZKP検証（必要に応じた利用） |

### **3.1 インタラクションフロー：信頼のライフサイクル**

1.  **オンボーディング（アカウント作成）**: ユーザーはアプリをダウンロードし、生体認証（FaceID/TouchID）を用いてPasskeyを作成する。裏側ではERC-4337スマートアカウントがデプロイされる。既存のEOAを持つユーザーに対しては、**EIP-7702** を用いてアカウント機能をアップグレードするパスも提供する。
2.  **KYCとクレデンシャル発行（Issuance）**: ユーザーは身分証（マイナンバーカード等）を用いてeKYCを行う。Goバックエンドは認証成功を確認し、OID4VCIプロトコルを通じて「Verified Fan VC」を発行する。
3.  **チケット購入とSBTミント**: ユーザーはチケットを購入する。バックエンドは決済を確認後、ユーザーのスマートアカウントに対してSBTをミントする。このSBTは譲渡不可能（Locked）な状態で発行される。
4.  **入場（Verification）**: ユーザーは会場でアプリを開き、ZKPを生成する。「私はこのイベントのSBTを所有しており、かつ有効なVCを持つ実在の人間である」ことを証明するQRコードを表示。スキャナーがこれを検証し、入場を許可する。

## **4. コンポーネント詳細解説：ERC-4337/EIP-7702 と Passkey**

2026年において、一般消費者に「シードフレーズ（秘密鍵）」の管理を強いるUXは許容されない。本システムでは、**ERC-4337（アカウント抽象化）** または **EIP-7702（EOAコード割り当て）** と **Passkey（WebAuthn）** を組み合わせることで、Web2ライクな使い勝手とWeb3のセキュリティを両立する。

> [!NOTE]
> **EIP-7702の採用**: 2026年時点では、新規ユーザーにはERC-4337ベースのSmart Accountを提供し、既にMetaMask等のEOAを所有するユーザーにはEIP-7702を活用して、既存アドレスのままPasskey署名やガス代代行の恩恵を受けられるハイブリッド戦略を採用する。

### **4.1 RIP-7212 (P256 Precompile) の導入とガス代革命**

従来、iPhoneのSecure EnclaveやAndroidのKeystoreで使用される暗号曲線 secp256r1 (P-256) の署名をEVM上で検証するには、約30万ガスという莫大なコストがかかっていた。しかし、2025年から2026年にかけて、Base、Optimism、Arbitrumなどの主要L2チェーンにおいて **RIP-7212** が実装された。

RIP-7212は、`0x100` という特定のアドレスにプリコンパイルコントラクトを配置し、P-256署名の検証をわずか **3,450ガス** で実行可能にする。これにより、スマートコントラクトウォレット（Smart Account）が、モバイルデバイスの生体認証器によって生成された署名を、ネイティブかつ低コストで検証できるようになった。

### **4.2 フロントエンド実装 (TypeScript)**

フロントエンドでは、`permissionless.js` と `viem` を使用して、スマートアカウントのクライアントを構築する。署名者（Signer）としてWebAuthn（Passkey）を利用する。

#### **4.2.1 WebAuthn Signer の構築**

まず、ユーザーのデバイスでPasskeyを作成し、それをスマートアカウントの所有権限（Owner）として登録する。

```typescript
// TypeScript: viemとpermissionless.jsを用いたWebAuthn Signerの実装例

import { toWebAuthnAccount } from "viem/account-abstraction";
import { createSmartAccountClient } from "permissionless";
import { entryPoint07Address } from "viem/account-abstraction";
import { http, createPublicClient } from "viem";
import { base } from "viem/chains";

// 1. WebAuthnアカウント（Passkey）の作成
// ブラウザ/OSのネイティブAPIを呼び出し、公開鍵ペアを生成
const webAuthnAccount = await toWebAuthnAccount({
  credential: {
    id: "credential-id-from-storage", // 保存されたクレデンシャルID
    name: "Ticket App User",
    publicKey: "...", // 公開鍵データ
  },
  // 2026年現在、PRF拡張により決定的署名もサポートされているが、
  // AAの署名検証には通常のWebAuthn署名フローを使用する。
});

// 2. スマートアカウントクライアントの初期化
// Kernel v3 または Safe v1.4.1+ (P256モジュール付き) を想定
// EIP-7702対応の場合は experimental_7702 パラメータなどを利用
const smartAccountClient = createSmartAccountClient({
  account: webAuthnAccount,
  entryPoint: {
    address: entryPoint07Address, // 2026年の標準であるv0.7を使用
    version: "0.7",
  },
  bundlerTransport: http("https://api.pimlico.io/v2/base/rpc"), // Bundlerエンドポイント
  chain: base, 
});

// 3. トランザクション（UserOperation）の送信
const txHash = await smartAccountClient.sendTransaction({
  to: ticketContractAddress,
  data: encodedMintData,
  value: 0n,
});
```

この実装において、`permissionless.js` は ERC-4337 v0.7 の仕様に準拠した UserOperation を構築し、署名（Passkeyによる署名）を付与してBundlerに送信する役割を担う。

### **4.3 バックエンド Paymaster (Go)**

ユーザーにガス代（ETH）を持たせない「ガスレス体験」を提供するために、**Verifying Paymaster** を導入する。Goバックエンドは、Paymasterの署名役として機能し、ユーザーからのリクエストを検証した上でガス代を肩代わりする。

**GoによるPaymaster署名ロジック:** Goバックエンドは `/api/rpc/paymaster` エンドポイントを公開し、フロントエンドから送られてきた UserOperation を検証する。ここで重要なのは、**呼び出そうとしている関数が許可されたもの（例: mintTicket, enterVenue）であるか** をデコードして確認することである。

```go
// Go: Paymasterサービスの実装概念

import (
    "github.com/ethereum/go-ethereum/common"
    "github.com/ethereum/go-ethereum/crypto"
    // その他、ERC-4337関連のライブラリ
)

func SignPaymasterOp(userOp UserOperation) ([]byte, error) {
    // 1. CallDataのデコード
    // ユーザーが実行しようとしているトランザクションの内容を解析
    method, err := ticketContractAbi.MethodById(userOp.CallData[:4])
    if err != nil {
        return nil, fmt.Errorf("invalid method")
    }

    // 2. ポリシーチェック
    // 「mintTicket」メソッドかつ、対象コントラクトが正規のものであるか確認
    if method.Name != "mintTicket" || userOp.Sender != expectedContract {
        return nil, fmt.Errorf("policy violation")
    }

    // 3. Rate Limit (RLN) チェック
    // スパム攻撃を防ぐため、同一ユーザーからの頻繁なリクエストを拒否

    // 4. Paymaster秘密鍵による署名
    // ERC-4337 v0.7では、paymasterAndDataに有効期限(validUntil/validAfter)が含まれる
    // 署名対象のハッシュを生成し、Paymasterの秘密鍵で署名する
    signature, err := paymasterKey.Sign(userOpHash)
      
    // paymasterAndDataの構築: [Address] + [ValidUntil] + [ValidAfter] + [Signature]
    return BuildPaymasterAndData(paymasterAddr, validUntil, validAfter, signature), nil
}
```

## **5. コンポーネント詳細解説：分散型ID (DID) と Verifiable Credentials (VC)**

本システムの法的準拠性の中核をなすのが **Verifiable Credential (VC)** である。VCは、ユーザーがKYC（本人確認）を通過したという事実を、個人情報を明かすことなく証明するためのデジタル証明書である。

### **5.1 OID4VCI (OpenID for Verifiable Credential Issuance)**

2026年現在、VC発行のデファクトスタンダードは **OID4VCI (OpenID for Verifiable Credential Issuance)** である。これはOAuth 2.0をベースにしたプロトコルであり、既存の認証基盤との親和性が高い。

### **5.2 GoバックエンドによるIssuer実装**

Go言語によるバックエンドでは、`trustbloc/wallet-sdk` や `hyperledger/aries-framework-go`（ただし2026年現在はOpenWallet Foundation傘下の最新ライブラリを推奨）を用いてIssuer機能を実装する。

**発行フロー:**

1.  **Authorization Request**: ユーザー（Wallet）は、バックエンドの認証エンドポイントに対してアクセストークンを要求する。ここでeKYCプロバイダーとの連携が行われる。
2.  **Credential Offer**: バックエンドはユーザーに対し、発行可能なクレデンシャル（例: VerifiedFanCredential）のオファーを提示する。
3.  **Credential Request**: Walletは自身のDID（`did:pkh:...` や `did:key:...`）を含めて署名し、クレデンシャル発行を要求する。
4.  **Issuance**: バックエンドはVCを作成し、Issuerの秘密鍵で署名して返却する。

**Go実装のポイント:** Issuerサービスは、ユーザーの個人情報（PII）をデータベースに保存せず、**ハッシュ値**（Salt付き）のみをVCに含めるか、あるいは「18歳以上である」「日本居住者である」といったブール値（述語）のみを含める設計とする。

```go
// Go: VC構築のロジック例 (trustbloc/wallet-sdkライクな構造)

func (s *Server) IssueCredential(w http.ResponseWriter, r *http.Request) {
    // アクセストークンの検証 (OAuth 2.0)
    // ...

    // VCの構築
    vc := &verifiable.Credential{
        Context: []string{
            "https://www.w3.org/2018/credentials/v1",
            "https://schema.ticket-system.jp/v1", // カスタムスキーマ
        },
        Type: []string{"VerifiableCredential", "VerifiedFanCredential"},
        Subject: map[string]interface{}{
            "id": userDID, // ユーザーのDID (Smart Account Address等)
            "complianceLevel": "JP_RESALE_ACT_TIER1", // 法的準拠レベル
            "isHuman": true,
        },
        Issuer: s.IssuerDID,
        Issued: time.Now(),
    }

    // VCへの署名 (Ed25519 または ES256)
    signedVC, err := s.signer.SignCredential(vc)
    if err != nil {
        http.Error(w, "Failed to sign VC", http.StatusInternalServerError)
        return
    }

    // OID4VCIレスポンス形式で返却
    json.NewEncoder(w).Encode(CredentialResponse{Credential: signedVC})
}
```

### **5.3 VCのフォーマットとSD-JWT**

プライバシー保護の観点から、**SD-JWT (Selective Disclosure JWT)** の採用を推奨する。SD-JWTを使用することで、ユーザーはVC提示時に「complianceLevel」のみを開示し、その他の属性（もし含まれていれば）を隠蔽することができる。これにより、過剰な情報開示を防ぎつつ、必要な法的要件（本人確認済みであること）のみを証明できる。

## **6. コンポーネント詳細解説：チケットSBT (ERC-5192)**

チケットは **Soulbound Token (SBT)** として実装する。通常のNFT（ERC-721）とは異なり、譲渡機能を制限することで、プロトコルレベルでの不正転売を物理的に不可能にする。

### **6.1 スマートコントラクト実装 (Solidity / OpenZeppelin v5)**

**ERC-5192 (Minimal Soulbound NFTs)** 標準に準拠する。この標準は、トークンがロックされているかどうかを外部から確認するためのインターフェース (`locked` 関数とイベント) を提供する。
OpenZeppelin v5 では、従来の `_beforeTokenTransfer` フックが廃止され、`_update` 関数に統合された点に注意が必要である。

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

// ERC-5192 インターフェース定義
interface IERC5192 {
    event Locked(uint256 tokenId);
    event Unlocked(uint256 tokenId);
    function locked(uint256 tokenId) external view returns (bool);
}

contract TicketSBT is ERC721, IERC5192, Ownable {
    // トークンごとのロック状態管理（本システムでは原則すべてTrue）
    mapping(uint256 => bool) private _locked;

    constructor(string memory name, string memory symbol) 
        ERC721(name, symbol) 
        Ownable(msg.sender) 
    {}

    function locked(uint256 tokenId) external view override returns (bool) {
        return _locked[tokenId];
    }

    // OpenZeppelin v5 のフック関数オーバーライド
    function _update(address to, uint256 tokenId, address auth) internal override returns (address) {
        address from = _ownerOf(tokenId);

        // ミント (from == 0) と バーン (to == 0) は許可
        // 通常の転送 (from != 0 && to != 0) は禁止
        if (from != address(0) && to != address(0)) {
            revert("SBT: Ticket transfer is prohibited by protocol");
        }

        // ミント時にロックイベントを発行
        if (from == address(0) && to != address(0)) {
            _locked[tokenId] = true;
            emit Locked(tokenId);
        }

        return super._update(to, tokenId, auth);
    }

    function mint(address to, uint256 tokenId) external onlyOwner {
        _mint(to, tokenId);
    }
      
    // 興行主（Owner）のみが実行可能な強制焼却（リセール用）
    function revoke(uint256 tokenId) external onlyOwner {
        _burn(tokenId);
    }
}
```

### **6.2 公認リセール（Authorized Resale）メカニズム**

SBTによる譲渡禁止は強力だが、病気や急用で参加できなくなったユーザーのための救済措置が必要である。これは「公認リセール」機能として実装する。

1.  **リセール申請**: ユーザーはアプリから「リセール申請」を行う。
2.  **エスクロー**: システムは対象のSBTをバーン（焼却）し、チケットを「販売可能プール」に戻す。
3.  **再販売**: 別のユーザーが定価で購入すると、システムは新しいSBTを新規購入者にミントする。
4.  **返金**: 元の所有者には、手数料を差し引いた定価相当額が返金される。

このプロセスにより、チケットの移動は常にコントラクト（興行主）を介して行われ、定価取引が強制されるため、スキャルピングの余地が完全に排除される。

## **7. コンポーネント詳細解説：プライバシーと入場認証 (ZKP)**

本システムの最大の技術的ハイライトは、入場時の認証に **Zero-Knowledge Proofs (ZKP)** を用いる点である。これは、チケットの所有権証明と二重使用の防止を、個人情報を一切明かすことなく行うための仕組みである。

### **7.1 Proof of Ownership の課題と解決策**

従来のQRコードチケットは、スクリーンショットを取るだけで複製が可能だった。動的QRコード（SafeTix）は有効だが、オフライン環境に弱く、中央サーバーへの依存度が高い。
本システムでは、**Semaphore** プロトコル の概念を拡張利用する。

*   **Identity**: ユーザーのデバイス内に生成された秘密の値（Trapdoor + Nullifier）。
*   **Membership**: チケットを購入した時点で、ユーザーの Identity Commitment（ハッシュ値）がオンチェーンの Merkle Tree に追加される。
*   **Proof**: 入場時、ユーザーは「私はこの Merkle Tree に含まれる Identity の秘密鍵を知っている」という証明（Proof）を生成する。

### **7.2 Double-Entry 防止のための Nullifier**

ZKPの特性上、同じ証明を何度でも生成できてしまう。これを防ぐために **Nullifier（無効化子）** を使用する。

*   **External Nullifier**: イベントID（例: Event_2026_TokyoDome_Day1）を一意の識別子として定義する。
*   **Nullifier Hash**: 回路内で Hash(IdentityNullifier, ExternalNullifier) を計算し、Proofの出力（Public Signal）として公開する。

スキャナー（Verifier）は、提示された Nullifier Hash をデータベース（Redis等）と照合する。

*   初めて提示されたHash → **入場OK**（DBにHashを記録）
*   既に存在するHash → **入場NG**（二重使用検知）

この仕組みにより、ユーザーのIdentityは隠蔽されたまま（Hashの一方向性）、特定のイベントに対して「1回限り」の入場権を行使できる。

### **7.3 フロントエンド ZKP 実装 (TypeScript + Circom / SP1)**

2026年、モバイルデバイスの演算能力向上により、スマートフォン上での証明生成（Client-Side Proving）は実用的な速度（数秒以内）で動作する。React Native環境では `mopro` や `snarkjs` のネイティブバインディングを利用する。

また、複雑なロジックをRustで記述できる **SP1** や **RISC Zero** といったzkVMも台頭しており、バックエンド検証や一部の高度なクライアント証明においてはこれらを併用することで開発生産性を向上させる。

**Circom回路設計（概念）:**

```c
template TicketCheck(nLevels) {
    // Private Inputs (秘密情報)
    signal input identityNullifier;
    signal input identityTrapdoor;
    signal input treePathIndices[nLevels];
    signal input treeSiblings[nLevels];

    // Public Inputs (公開情報)
    signal input externalNullifier; // イベントID
    signal input root;              // 現在のSBTコントラクトのMerkle Root

    // Outputs
    signal output nullifierHash;

    // 1. Identity Commitmentの再構築
    component commitmentHasher = Poseidon(2);
    commitmentHasher.inputs[0] <== identityNullifier;
    commitmentHasher.inputs[1] <== identityTrapdoor;
      
    // 2. Merkle Treeの包含証明 (Membership Proof)
    component treeVerifier = MerkleTreeInclusionProof(nLevels);
    treeVerifier.leaf <== commitmentHasher.out;
    treeVerifier.root <== root;
    for (var i = 0; i < nLevels; i++) {
        treeVerifier.pathIndices[i] <== treePathIndices[i];
        treeVerifier.siblings[i] <== treeSiblings[i];
    }

    // 3. Nullifier Hashの生成 (二重使用防止用)
    component nullifierHasher = Poseidon(2);
    nullifierHasher.inputs[0] <== identityNullifier;
    nullifierHasher.inputs[1] <== externalNullifier;
      
    nullifierHash <== nullifierHasher.out;
}
```

**TypeScriptによる証明生成:**

```typescript
import { generateProof } from "@semaphore-protocol/proof";

// 入場ボタン押下時の処理
async function generateEntryProof(
  identity: Identity, 
  merkleProof: MerkleProof, 
  eventId: string
) {
  // クライアントサイドでの証明生成
  // snarkjsを利用してwasmとzkeyからproofを作成
  const fullProof = await generateProof(
    identity,
    merkleProof,
    eventId, // External Nullifier
    "entry-signal", // Signal
    {
      zkeyFilePath: "./circuits/ticket.zkey",
      wasmFilePath: "./circuits/ticket.wasm"
    }
  );
    
  // 生成されたProofとPublic SignalsをQRコード化して表示
  return fullProof;
}
```

## **8. 実装ロードマップと統合戦略**

### **8.1 開発フェーズと優先順位**

1.  **Phase 1: コアコントラクト開発 (Solidity)**
    *   ERC-5192準拠のSBT、およびMerkle Tree管理機能の実装。
    *   RIP-7212対応のSmart Accountモジュールの選定（Kernel/Safe）。
2.  **Phase 2: バックエンド認証基盤 (Go)**
    *   OID4VCI Issuerサービスの構築。KYCプロバイダーAPIとの結合。
    *   Paymasterサービスの構築。UserOpの検証ロジックの実装。
3.  **Phase 3: ZK回路とモバイルアプリ (Circom/Rust/TS)**
    *   TicketCheck回路の設計（CircomまたはSP1）とTrusted Setupの実施。
    *   React NativeアプリへのProver組み込みとパフォーマンスチューニング。
4.  **Phase 4: 統合テストと監査**
    *   Goバックエンドの高負荷試験（チケット発売時のスパイク対応）。
    *   スマートコントラクトのセキュリティ監査。

### **8.2 データモデルとストレージ戦略 (Go/PostgreSQL)**

オンチェーンには最小限のデータ（Commitment Root, SBT Ownership）のみを記録し、メタデータやNullifier履歴はオフチェーンDBで管理する。

| テーブル名 | 役割 | 保存データ |
| :---- | :---- | :---- |
| users | ユーザー管理 | UserDID, SmartAccountAddress, KYCStatus (Flag only) |
| tickets | チケットメタデータ | TokenID, EventID, SeatNumber, Status (Active/Burned) |
| nullifiers | 入場履歴管理 | NullifierHash, EventID, Timestamp (Replay Attack防止用) |
| merkle_tree | ツリー構造キャッシュ | LeafIndex, CommitmentHash (Proof生成の高速化用) |

### **8.3 インフラストラクチャとスケーラビリティ**

*   **L2選定**: Base、Optimism、Arbitrum等のRollupチェーンを採用。RIP-7212のサポート状況とガス代の安定性が選定基準となる。
*   **Bundler**: Pimlico や Stackup などの商用Bundlerサービスを利用しつつ、バックアップとして自社運用のBundlerノードを用意する。
*   **ZK Proving**: モバイルでの生成が基本だが、低スペック端末向けに「Delegated Proving（委任証明）」サーバーを用意することも検討に値する（ただし、秘密鍵の送信が必要になるため、セキュリティトレードオフの慎重な検討が必要）。

## **9. 結論**

本レポートで提示したアーキテクチャは、2026年の技術水準において、法的要件（チケット不正転売禁止法）とユーザーの権利（プライバシー、利便性）を高度にバランスさせる唯一の解である。
**SBT**による物理的な転売抑止、**DID/VC**によるコンプライアンス準拠、**ERC-4337/EIP-7702**によるシームレスなUX、そして**ZKP**によるプライバシー保護。これら4つの技術の融合は、単なるチケットシステムの枠を超え、次世代のデジタル資産管理とアイデンティティ証明の標準モデルとなる可能性を秘めている。
開発チームは、特に **Go言語によるOID4VCI Issuerの実装** と **モバイルアプリでのZKP生成パフォーマンス** に注力し、実運用に耐えうる堅牢なシステムを構築することが求められる。

### **主要技術要約テーブル**

| 技術領域 | 標準規格 | システム内での役割 | 2026年の重要機能・動向 |
| :---- | :---- | :---- | :---- |
| **Account** | ERC-4337 / EIP-7702 | ユーザーウォレット基盤 | **RIP-7212** (P256 Precompile) 対応と **AuthZ** (EOA拡張) |
| **Identity** | W3C DID / VC | 法的本人確認 (KYC) | **OID4VCI** による標準化された発行フロー |
| **Ticket** | ERC-5192 | チケット資産定義 | **locked** ステータスによるプロトコルレベルの譲渡禁止 |
| **Privacy** | ZKP (Groth16/SP1) | 入場時の所有権証明 | **Client-side proving** (モバイル生成) による非監視型認証 |
| **Anti-Spam** | Semaphore / RLN | 二重入場防止 | **Nullifier Hash** による一意性制約の強制 |

### **10. 技術選定の更新に関する補足 (2026年版)**

今回の改訂において、以下の最新技術標準を追加・採用した背景と意図を補足する。

#### **10.1 EIP-7702 (Authorized EOAs) の採用について**
**背景:**
従来のERC-4337（Account Abstraction）は、新規ユーザーには優れたUXを提供するものの、既にMetaMaskなどのEOA（Externally Owned Account）を保有しているWeb3ユーザーにとっては、新しいアドレス（Smart Account）を作成・管理する必要があり、資産や履歴の分断を生む課題があった。

**採用理由:**
EIP-7702は、既存のEOAに対してスマートコントラクトの機能（ガス代代行、バッチ処理、セキュリティガード等）を一時的に「割り当てる」ことを可能にする。これにより、ライトユーザーには完全なAAウォレットを提供しつつ、既存のクリプトユーザーには**普段使用しているウォレットのまま**、Passkey認証やガスレス体験を提供することが可能となる。このハイブリッド戦略により、あらゆる層のユーザーに対して最適なオンボーディング体験を実現する。

#### **10.2 zkVM (SP1 / RISC Zero) の導入について**
**背景:**
ZKP回路の開発言語であるCircomは、制約（Constraints）を直接記述する低レイヤー言語であり、複雑な条件分岐やループを含むビジネスロジックの実装・監査の難易度が極めて高かった。

**採用理由:**
2025年以降に急成長したzkVM（特にSP1やRISC Zero）は、Rustなどの標準的なプログラミング言語で記述されたロジックをゼロ知識証明化することを可能にする。
本システムでは、モバイル端末での証明生成速度がクリティカルな**入場ゲート認証**部分には、引き続き回路サイズが最小化可能な**Circom/Mopro**を採用する。一方で、より複雑な**購入資格判定**（例: ファンクラブ会員ランクと過去の購入履歴を組み合わせた動的な条件）などの検証には、開発効率と保守性に優れた**zkVM**を活用する「適材適所」のアーキテクチャを採用することで、システムの柔軟性と信頼性を向上させる。

### **引用文献**

#### **Works cited**

1.  Act on Ensuring the Proper Distribution of Show and Event Tickets by Prohibiting the Unauthorized Resale of Specified Show and Event Tickets - Japanese Law Translation, [https://www.japaneselawtranslation.go.jp/en/laws/view/3356/en](https://www.japaneselawtranslation.go.jp/en/laws/view/3356/en)
2.  Japan: Law to Regulate Ticket Resales Enacted | Library of Congress, [https://www.loc.gov/item/global-legal-monitor/2019-01-24/japan-law-to-regulate-ticket-resales-enacted/](https://www.loc.gov/item/global-legal-monitor/2019-01-24/japan-law-to-regulate-ticket-resales-enacted/)
3.  Ticket scalping laws come into effect in Japan ahead of Tokyo 2020 - Inside The Games, [https://www.insidethegames.biz/articles/ticket-scalping-laws-come-into-effect-in-japan-ahead-of-tokyo-2020](https://www.insidethegames.biz/articles/ticket-scalping-laws-come-into-effect-in-japan-ahead-of-tokyo-2020)
4.  Harness the Power of SafeTix™ in 2025 - Ticketmaster Business, [https://business.ticketmaster.com/harness-the-power-of-safetix-in-2025/](https://business.ticketmaster.com/harness-the-power-of-safetix-in-2025/)
5.  Client-Side Proving | PSE - Privacy Stewards of Ethereum, [https://pse.dev/projects/client-side-proving](https://pse.dev/projects/client-side-proving)
6.  ZKP on the Client-side: Challenges & Our Solutions | by Shinobu Labs | Medium, [https://medium.com/@shinobu_labs/zkp-on-the-client-side-challenges-our-solutions-1c9a1647c8f9](https://medium.com/@shinobu_labs/zkp-on-the-client-side-challenges-our-solutions-1c9a1647c8f9)
7.  What is RIP-7212? Precompile for secp256r1 Curve Support - Alchemy, [https://www.alchemy.com/blog/what-is-rip-7212](https://www.alchemy.com/blog/what-is-rip-7212)
8.  What is RIP-7212? | Eco Support Center, [https://eco.com/support/en/articles/10714109-what-is-rip-7212](https://eco.com/support/en/articles/10714109-what-is-rip-7212)
9.  Permissionless.js Detailed Guide - Safe Docs, [https://docs.safe.global/advanced/erc-4337/guides/permissionless-detailed](https://docs.safe.global/advanced/erc-4337/guides/permissionless-detailed)
10. Permissionless.js Quickstart Guide - Safe Docs, [https://docs.safe.global/advanced/erc-4337/guides/permissionless-quickstart](https://docs.safe.global/advanced/erc-4337/guides/permissionless-quickstart)
11. OpenID4VC, DCQL and OpenID Federation: Three new fundamental TypeScript projects incubated at OpenWallet Foundation, [https://openwallet.foundation/2025/02/25/openid4vc-dcql-and-openid-federation-three-new-fundamental-typescript-projects-incubated-at-openwallet-foundation/](https://openwallet.foundation/2025/02/25/openid4vc-dcql-and-openid-federation-three-new-fundamental-typescript-projects-incubated-at-openwallet-foundation/)
12. OpenID for Verifiable Credential Issuance 1.0, [https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html](https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html)
13. openwallet-foundation-labs/oid4vc-ts: OpenID for Verifiable Credentials - TypeScript, [https://github.com/openwallet-foundation-labs/oid4vc-ts](https://github.com/openwallet-foundation-labs/oid4vc-ts)
14. openid4ci package - github.com/trustbloc/wallet-sdk/pkg/openid4ci - Go Packages, [https://pkg.go.dev/github.com/trustbloc/wallet-sdk/pkg/openid4ci](https://pkg.go.dev/github.com/trustbloc/wallet-sdk/pkg/openid4ci)
15. The community stack — walt.id, [https://walt.id/blog/p/community-stack](https://walt.id/blog/p/community-stack)
16. Reference implementation of ERC5192 Minimal Soulbound Tokens - GitHub, [https://github.com/attestate/ERC5192](https://github.com/attestate/ERC5192)
17. FINAL EIP-5192 - Minimal Soulbound NFTs - Ethereum Magicians, [https://ethereum-magicians.org/t/final-eip-5192-minimal-soulbound-nfts/9814](https://ethereum-magicians.org/t/final-eip-5192-minimal-soulbound-nfts/9814)
18. Soulbound NFTs in ERC721 version 5.0+ - Smart Contracts - OpenZeppelin Forum, [https://forum.openzeppelin.com/t/soulbound-nfts-in-erc721-version-5-0/41550](https://forum.openzeppelin.com/t/soulbound-nfts-in-erc721-version-5-0/41550)
19. openzeppelin-contracts-upgradeable/CHANGELOG.md at master - GitHub, [https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/blob/master/CHANGELOG.md](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/blob/master/CHANGELOG.md)
20. Ticket Resale Prohibition Act - Jasumo Tickets, [https://jasumotickets.com/ticket-resale-prohibition-act/](https://jasumotickets.com/ticket-resale-prohibition-act/)
21. Velocity reduction — The cryptoeconomic speed bumps of the GET Protocol | Part 1 | by Olivier Biggs | Open Ticketing Ecosystem | Medium, [https://medium.com/get-protocol/velocity-reduction-the-cryptoeconomic-speed-bumps-of-the-get-protocol-part-1-282c0b3e7004](https://medium.com/get-protocol/velocity-reduction-the-cryptoeconomic-speed-bumps-of-the-get-protocol-part-1-282c0b3e7004)
22. semaphore-protocol/semaphore: A zero-knowledge protocol for anonymous interactions. - GitHub, [https://github.com/semaphore-protocol/semaphore](https://github.com/semaphore-protocol/semaphore)
23. Semaphore proofs, [https://docs.semaphore.pse.dev/guides/proofs](https://docs.semaphore.pse.dev/guides/proofs)
24. Mopro x Noir: Powering Mobile Zero-Knowledge Proofs, [https://zkmopro.org/blog/noir-integraion/](https://zkmopro.org/blog/noir-integraion/)
25. 収納代行業に許認可制度はある？改正資金決済法の規制対象についても解説, [https://biz.moneyforward.com/establish/basic/71476/](https://biz.moneyforward.com/establish/basic/71476/)
