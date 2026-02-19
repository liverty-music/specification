# Liverty Music UI/UX Design Analysis Report

**Date:** 2026-02-16
**Scope:** Full codebase analysis of all frontend templates, CSS, and TypeScript files
**Reference:** `specification/openspec/changes/archive/2026-02-15-interactive-artist-onboarding/docs/onboarding-ux.md`

---

## Executive Summary

現在のUIは**機能的には仕様を概ねカバー**しているが、ビジュアルデザインの質が「プロトタイプレベル」にとどまっている。UX仕様書が目指す「ワクワク感」「ゲーミフィケーション」「没入感」は、コードレベルでは部分的にしか実現されていない。以下、画面ごとに問題を洗い出す。

---

## 1. Welcome Page（ファーストビュー）

### 現状

```
┌──────────────────────────────────┐
│                                  │
│                                  │
│   大好きなあのバンドのライブ、    │
│   もう二度と見逃さない。          │
│                                  │
│   あなたの推しアーティストを...   │
│                                  │
│   ┌──────────────────────────┐   │
│   │      Sign Up (blue)      │   │
│   └──────────────────────────┘   │
│   ┌──────────────────────────┐   │
│   │      Sign In (gray)      │   │
│   └──────────────────────────┘   │
│                                  │
└──────────────────────────────────┘
```

### 問題点

| # | Category | Issue | Severity |
|---|----------|-------|----------|
| W-1 | **CTA Design** | UX仕様は「`[Continue with Google]`ボタンのみ」と明記。現状は`Sign Up`/`Sign In`の2ボタン構成で、Googleブランドが一切ない | **Critical** |
| W-2 | **Visual Impact** | Hero Copyのフォントが`text-3xl`(30px)でtext-gray-900。音楽サービスのLPとしては地味すぎる。背景が白一色 | **High** |
| W-3 | **Brand Identity** | 「Liverty Music」のロゴ・サービス名がどこにもない。`<title>Aurelia</title>`のまま | **Critical** |
| W-4 | **Background** | 真っ白な背景。音楽サービスらしさゼロ。ダークテーマやグラデーション背景がない | **High** |
| W-5 | **Animation** | ファーストビューにアニメーションが一切ない。Hero Copy のフェードイン、パーティクルエフェクト等がない | **Medium** |
| W-6 | **Social Proof** | 「信頼の要素」がない。ユーザー数、対応アーティスト数、「30秒でセットアップ完了」等の補助情報がない | **Low** |
| W-7 | **Mobile UX** | ボタンの`min-h-[48px]`は適切だが、ページ全体のパディングが`px-4`のみで、縦方向のリズムに変化がない | **Medium** |

---

## 2. App Shell（全体レイアウト）

### 現状

```
┌──────────────────────────────────────────┐
│ Welcome  About           Sign In Sign Up │  ← nav bar
├──────────────────────────────────────────┤
│                                          │
│           <au-viewport>                  │
│                                          │
└──────────────────────────────────────────┘
```

### 問題点

| # | Category | Issue | Severity |
|---|----------|-------|----------|
| A-1 | **Nav Design** | `background: #eee` + `a { padding: 10px }` — 完全にデフォルトのHTMLスタイル。Tailwindクラスと生CSSが混在 | **Critical** |
| A-2 | **Auth Controls** | `auth-status.html`に3色ボタン（blue/green/red）が並び、統一感がない。信号機のような配色 | **High** |
| A-3 | **Navigation UX** | 「Welcome」「About」のリンクが常時表示。オンボーディングフロー中にこれが見えると離脱リスクあり | **High** |
| A-4 | **CSS Architecture** | `my-app.css`に`nav { background: #eee }`等の生CSSが残っている。Tailwind v4を使っているのに一貫性がない | **Medium** |
| A-5 | **Page Title** | `<title>Aurelia</title>` — scaffold名がそのまま。`Liverty Music`にすべき | **Critical** |
| A-6 | **Favicon/PWA** | favicon, apple-touch-icon, manifest.json が未設定。PWA仕様にも関わらずPWA対応がない | **High** |
| A-7 | **Font** | カスタムフォント未設定。system-uiのみ。音楽サービスとしてのブランド感が出ない | **Medium** |

---

## 3. Artist Discovery（Bubble UI / DNA Extraction）

### 現状の良い点
- Matter.js物理演算でバブルが浮遊 ✓
- DNA Orbのグラスエフェクト（radial gradient、specular highlight）✓
- 吸い込みアニメーション（Bezier curve + dissolve particles）✓
- パフォーマンス監視・品質自動調整 ✓
- キーボードナビゲーション対応 ✓
- 類似アーティスト分裂（spawnBubblesAt）✓

### 問題点

| # | Category | Issue | Severity |
|---|----------|-------|----------|
| D-1 | **Bubble Visual** | バブルが全て同じ紫系グラデーション(`hsl(260/250/240)`)。アーティストごとの個性がない。仕様書では「テーマカラー」生成を要求 | **High** |
| D-2 | **Bubble Size** | 全バブルが`artist.radius`で表示されるが、人気度・知名度による差別化が不明確 | **Medium** |
| D-3 | **Complete Button** | `View Live Schedule (X artists)` — 仕様書では `[ライブ日程を見る (◯組)]` or `[ダッシュボードを作成する (◯組フォロー中)]`。英語でテキストが仕様と不一致 | **Medium** |
| D-4 | **Orb Label** | 「Music DNA オーブ」のテキストラベルがない。ユーザーはオーブが何なのか分からない | **High** |
| D-5 | **Haptic Feedback** | フォロー時のバイブレーション（Vibration API）がない。ゲーム感覚の体験に不足 | **Low** |
| D-6 | **Sound Effect** | フォロー時のサウンドエフェクトがない（これはMVP外でもいいが、ワクワク感に大きく影響する） | **Low** |
| D-7 | **Onboarding Guidance** | 初回時の操作ガイド（「バブルをタップしてアーティストをフォロー」的なチュートリアル）がない | **High** |
| D-8 | **Counter Animation** | フォロー数カウンターのアニメーションがない。数字がパッと変わるだけ | **Medium** |
| D-9 | **Empty State** | バブルが全て吸い込まれた場合の処理が未定義 | **Low** |
| D-10 | **Background Depth** | 背景のグラデーション(`rgb(3 7 18) → rgb(49 46 129) → rgb(3 7 18)`)は良いが、星やパーティクル等の装飾がなく平坦 | **Medium** |

---

## 4. Loading Sequence（Benevolent Deception）

### 現状

```
┌──────────────────────────────────┐
│                                  │
│       (dark gradient bg)         │
│                                  │
│   「あなたのMusic DNAを構築中...」 │
│                                  │
│                                  │
└──────────────────────────────────┘
```

### 問題点

| # | Category | Issue | Severity |
|---|----------|-------|----------|
| L-1 | **Visual Richness** | テキストのみ。「単なるスピナーは禁止」とあるがそもそもスピナーすらない。プログレスバー、アイコン、パーティクル演出が皆無 | **Critical** |
| L-2 | **Phase Transition** | フェードイン/アウトのみ（opacity 0.8s）。ステップ進行感が弱い。進行率バーやステップインジケーターがない | **High** |
| L-3 | **Visual Continuity** | 前画面（Bubble UI）からのトランジションがない。突然テキスト画面になる | **High** |
| L-4 | **DNA Orb Reuse** | Bubble UIで構築したDNA Orbをこの画面で再表示すれば、世界観の連続性を保てるのにもったいない | **Medium** |
| L-5 | **Animation** | テキストの出現がopacity transitionのみ。typewriter effect、text reveal、glitch effect等の演出がない | **Medium** |
| L-6 | **Emoji** | Phase 3に🤖がハードコードされているが、Emojiに依存するデザインは環境差が出やすい | **Low** |

---

## 5. Dashboard - Live Highway

### 現状

```
┌──────────────────────────────────────────┐
│ Live Highway         My City Region Other│
├──────────────────────────────────────────┤
│ ─── Feb 20 ──────────────────────────────│
│ ┌──────────┐ ┌──────┐                    │
│ │          │ │Artist│ Artist Osaka        │
│ │  Artist  │ │ Name │                     │
│ │  Name    │ │福岡  │                     │
│ │(big card)│ └──────┘                     │
│ └──────────┘                              │
│ ─── Feb 22 ──────────────────────────────│
│ ...                                       │
└──────────────────────────────────────────┘
```

### 良い点
- 3列レイアウト（50%/30%/20%）は仕様通り ✓
- アーティスト名から一意カラー生成（HSLベース）✓
- Mega-typographyカード（`text-3xl font-extrabold`）✓
- ボトムシート詳細モーダル ✓
- Google Maps / Calendar連携 ✓

### 問題点

| # | Category | Issue | Severity |
|---|----------|-------|----------|
| H-1 | **Date Separator** | `bg-gray-50 border-b border-gray-200` — 地味すぎる。時間軸の視覚的重みが足りない | **Medium** |
| H-2 | **Card Design** | カードが`rounded-2xl`のフラットな単色矩形のみ。グラデーション、テクスチャ、影、微妙なパターンがない | **High** |
| H-3 | **Color Palette** | `artistColor()`は`hsl(hash, 70%, 45%)`で生成。彩度70%/明度45%は暗めで、カード間の視覚的区別が弱い可能性 | **Medium** |
| H-4 | **Typography** | Main laneのカードが`text-3xl`だが、「メガ・タイポグラフィ型」としてはまだ小さい。仕様の意図は画面幅いっぱいの巨大テキスト | **High** |
| H-5 | **Card Animation** | スクロール時のアニメーション（parallax, fade-in, stagger）がない。静的なリスト | **Medium** |
| H-6 | **Empty Lane** | 空レーンの表示が`—`（テキスト）のみ。視覚的に寂しい | **Low** |
| H-7 | **Header Design** | `Live Highway`のタイトルが`text-lg font-bold text-gray-900`。ブランド感がない | **Medium** |
| H-8 | **Scroll Indicator** | 「下にスクロール」のヒントがない。初回訪問でコンテンツの存在に気づかない可能性 | **Medium** |
| H-9 | **Pull-to-Refresh** | モバイルユーザーがデータ更新する手段がない | **Low** |
| H-10 | **Region Setup** | 仕様書ではダッシュボード初回表示時にエリア（居住地）入力を要求するが、そのUI/フローが見当たらない | **Critical** |

---

## 6. Event Detail Sheet（ボトムシート）

### 問題点

| # | Category | Issue | Severity |
|---|----------|-------|----------|
| S-1 | **Animation** | `transition-transform duration-300 ease-out`のみ。Spring animationやbounce effectがない | **Medium** |
| S-2 | **Swipe Gesture** | スワイプダウンで閉じるジェスチャーがない。backdrop tap のみ | **Medium** |
| S-3 | **Emoji Icons** | `📅` `📍` `🔗` がUnicode Emojiハードコード。SVGアイコンの方がデザインの一貫性が保てる | **Medium** |
| S-4 | **Button Design** | `bg-gray-900`の黒ボタン。音楽サービスらしいアクセントカラーがない | **Medium** |
| S-5 | **Share Button** | 共有機能がない。「友達に教える」はエンゲージメントに重要 | **Low** |

---

## 7. Toast Notification

### 問題点

| # | Category | Issue | Severity |
|---|----------|-------|----------|
| T-1 | **Design** | `bg-gray-900/90`の黒背景。仕様書では「🎫 [アーティスト名]のライブ予定あり！」という躍動感のあるデザインを要求 | **High** |
| T-2 | **Animation** | `translate-y` + `opacity` のみ。弾むような入場アニメーションがない | **Medium** |
| T-3 | **Duration** | 仕様書では「2〜3秒間だけ表示し、フェードアウト」。コードでの制御確認が必要 | **Low** |

---

## 8. Cross-Cutting Concerns（横断的問題）

| # | Category | Issue | Severity |
|---|----------|-------|----------|
| X-1 | **Design System** | カラーパレット、タイポグラフィスケール、スペーシングシステムが未定義。Tailwindのデフォルト値を場当たり的に使用 | **Critical** |
| X-2 | **Dark Mode** | Bubble UI/Loading は暗いが、Welcome/Dashboard/Detail は白背景。一貫性がない | **High** |
| X-3 | **CSS Architecture** | ShadowDOM CSS（loading-sequence）、Tailwind utility classes、生CSS（my-app.css）が混在。統一されていない | **High** |
| X-4 | **Transition** | 画面遷移アニメーションが一切ない。`router.load()`で瞬時切り替え | **High** |
| X-5 | **Font Loading** | カスタムWebフォント未使用。system-uiフォールバックのみ | **Medium** |
| X-6 | **Loading States** | Dashboard以外のローディング状態表現がない（skeleton screen等） | **Medium** |
| X-7 | **Error States** | エラー時のUI表現がconsole.error/logのみ。ユーザー向けエラーUIがほぼない | **Medium** |
| X-8 | **Accessibility** | Bubble UIのaria-label、keyboard navigationは良い。ただし色コントラスト比の検証が必要 | **Medium** |
| X-9 | **PWA** | manifest.json, service worker が未設定。仕様書ではPWAインストール要求が定義されている | **High** |
| X-10 | **Responsive** | 仕様書で「スマートフォンの縦画面で片手スクロール」を大前提としているが、PC幅の制限（`max-w-5xl`）で中途半端にPC対応している | **Medium** |

---

## 9. Missing Features（未実装機能）

| # | Feature | UX Spec Reference | Priority |
|---|---------|-------------------|----------|
| M-1 | **Region/Area Setup** | Step 4: 初回ダッシュボード表示時にエリア入力 | **Critical** |
| M-2 | **Google Sign-In Button** | Step 1: `[Continue with Google]`ボタン | **Critical** |
| M-3 | **Push Notification Permission** | Section 4: ライブカードタップ後に通知許可要求 | **High** |
| M-4 | **PWA Install Prompt** | Section 4: 2回目セッションでホーム画面追加案内 | **High** |
| M-5 | **Onboarding Tutorial** | Step 2: バブルUIの操作説明 | **Medium** |
| M-6 | **Progress Indicator (Loading)** | Step 3: ステップ進行型表示 | **Medium** |

---

## 10. Priority Matrix

```
                    IMPACT
                High ──────────── Low
           ┌────────────────────────────┐
    Quick  │ W-1, W-3, A-5    │ D-5,D-6│
    Wins   │ A-1, A-2         │ D-9    │
           │ T-1              │ S-5    │
           ├──────────────────┼────────┤
    Major  │ X-1, X-2, X-4   │ X-8    │
    Effort │ W-2, W-4, H-10  │ H-9    │
           │ L-1, D-1, D-7   │        │
           │ H-2, H-4, X-9   │        │
           └──────────────────┴────────┘
```

---

## 11. Recommended Action Plan

### Phase 1: Foundation（基盤整備）
1. **Design System定義** — カラーパレット、タイポグラフィ、スペーシング、シャドウのTailwind theme拡張
2. **Dark/Light テーマ統一** — 全画面をダークテーマに統一（音楽サービスの世界観）
3. **CSS Architecture統一** — ShadowDOM or Tailwind utility に一本化
4. **ブランド設定** — ロゴ、favicon、page title、カスタムフォント導入

### Phase 2: Critical UX Fixes
5. **Welcome Page刷新** — Google Sign-Inボタン、ダーク背景、Heroアニメーション
6. **App Shell リデザイン** — オンボーディング中はナビ非表示、認証状態UIの改善
7. **Region Setup Flow** — 初回ダッシュボード前のエリア入力画面追加
8. **Loading Sequence強化** — プログレスバー、ステップインジケーター、ビジュアル演出

### Phase 3: Polish（仕上げ）
9. **Bubble UI改善** — アーティスト個別カラー、操作ガイド、オーブラベル
10. **Dashboard強化** — カードデザイン改善、スクロールアニメーション、メガタイポグラフィ拡大
11. **画面遷移アニメーション** — ルート遷移のフェード/スライドアニメーション
12. **Toast/Detail Sheet改善** — 躍動感のあるアニメーション、SVGアイコン

### Phase 4: Engagement
13. **PWA対応** — manifest.json、Service Worker、インストールプロンプト
14. **Push通知** — コンテキスト付き許可フロー
15. **Haptic/Sound** — フォロー時の触覚・音声フィードバック

---

## Appendix: File Reference Map

| Screen | Template | CSS | TS |
|--------|----------|-----|-----|
| Welcome | `src/welcome-page.html` | (Tailwind inline) | `src/welcome-page.ts` |
| App Shell | `src/my-app.html` | `src/my-app.css` | `src/my-app.ts` |
| Auth Status | `src/components/auth-status.html` | (Tailwind inline) | `src/components/auth-status.ts` |
| Artist Discovery | `src/routes/artist-discovery/artist-discovery-page.html` | `src/routes/artist-discovery/artist-discovery-page.css` | `src/routes/artist-discovery/artist-discovery-page.ts` |
| DNA Orb | `src/components/dna-orb/dna-orb-canvas.html` | `src/components/dna-orb/dna-orb-canvas.css` | `src/components/dna-orb/dna-orb-canvas.ts` |
| Loading | `src/routes/onboarding-loading/loading-sequence.html` | `src/routes/onboarding-loading/loading-sequence.css` | `src/routes/onboarding-loading/loading-sequence.ts` |
| Dashboard | `src/routes/dashboard.html` | (Tailwind inline) | `src/routes/dashboard.ts` |
| Live Highway | `src/components/live-highway/live-highway.html` | (Tailwind inline) | `src/components/live-highway/live-highway.ts` |
| Event Card | `src/components/live-highway/event-card.html` | (Tailwind inline) | `src/components/live-highway/event-card.ts` |
| Detail Sheet | `src/components/live-highway/event-detail-sheet.html` | (Tailwind inline) | `src/components/live-highway/event-detail-sheet.ts` |
| Toast | `src/components/toast-notification/toast-notification.html` | (Tailwind inline) | `src/components/toast-notification/toast-notification.ts` |
