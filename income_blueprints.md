# RICKION · Income Blueprints

> These are real, simulation-validated revenue streams that Rickion can
> select, backtest, and graduate to live execution. Every blueprint has:
> startup cost, revenue model, simulation gate, ethical guard, execution
> path. Rickion reads this file before each "what should I build next"
> decision. Gemini alone can execute — no Claude needed for run-time.

**Core rule**: nothing goes live until Simulation Station has greenlit it
*and* Gidion has tapped APPROVE. Paper mode is fair game for Rickion alone.

---

## Tier 0 · Cost-covering (zero-budget start)

Rickion needs to pay its own VPS (~€6/mo) and API credits within 30 days.
These are low-risk, low-margin starters that cover base cost fast.

### 0.1 · Paid API wrappers on ai-saas-marketplaces
- **What**: Wrap Gemini with a specialized prompt ("Rick-grade cold outreach
  generator", "legal-compliant NDA summarizer", etc.), list on Rapid API /
  Rapid-API-alternatives, charge $0.002/call with 50% margin.
- **Startup cost**: €0 (Rickion writes the wrapper, deploys to same VPS).
- **Revenue model**: per-call microtransactions, direct Stripe payout.
- **Sim gate**: projected monthly calls × margin > €20/mo.
- **Ethical guard**: only wrap non-copyrighted, non-evasive use cases.
- **Execution**: Rickion writes the Flask endpoint, Rickion signs up Gidion
  on the marketplace (manual step), Rickion monitors + iterates prompts.

### 0.2 · Niche newsletter (AI-curated)
- **What**: Daily or weekly email on one narrow topic (e.g. "AI-automation
  arbitrage opportunities for EU SMBs"). Rickion writes it, sends via
  Buttondown or Substack, monetizes via paid tier + sponsor slots.
- **Startup cost**: €0 (Buttondown free tier, later €9/mo).
- **Revenue model**: €5/mo paid subs + €50-500/issue sponsor slots.
- **Sim gate**: Rickion simulates 30 issues, scores content density; if
  avg quality > 75/100, greenlit.
- **Ethical guard**: always disclose AI authorship in footer.

### 0.3 · Cold-outreach research-as-a-service
- **What**: Rickion finds 50 qualified prospects per week for a target
  company (based on their ICP), delivers via shared Notion. Charges
  €100/week per client. Low-touch — research done in Rickion's sleep.
- **Startup cost**: €0 (just Gemini credits).
- **Revenue model**: fixed weekly retainer, 3-5 clients covers VPS easy.
- **Sim gate**: Rickion generates a demo batch and self-scores quality >80.

---

## Tier 1 · Scaling (€500-5K budget)

### 1.1 · Crypto paper-to-live arbitrage
- **What**: Multi-exchange spread trading (already wired in Arbitrage Desk).
  Start paper-only 60 days. If Sharpe > 2, allocate small live capital.
- **Startup cost**: exchange fees (~€0 on read) + €500 seed live capital
  (Gidion's choice, minimum).
- **Revenue model**: expected 0.5-2% / month after fees at small size.
- **Sim gate**: 60d paper run with ≥200 trades, Sharpe ≥ 2, max DD < 3%.
- **Ethical guard**: never trade against retail on leverage; never market-make
  with user's name; taxable event logging auto.
- **Execution**: Rickion writes execution adapter per exchange, Gidion
  uploads API keys with *withdrawal disabled*, kill-switch file stops all.

### 1.2 · Programmatic SEO micro-site farm
- **What**: Build 1-3 sites that answer long-tail queries via AI-generated
  but human-verified pages. Monetize: AdSense + affiliate + lead-gen.
- **Startup cost**: €10/mo hosting, €10-20/mo domains.
- **Revenue model**: €200-2000/mo per mature site after 6 months.
- **Sim gate**: keyword research returns ≥500 low-competition queries in a
  niche, projected CPM × traffic estimate > €200/mo.
- **Ethical guard**: never impersonate a human expert; factcheck before pub.

### 1.3 · Niche SaaS micro-tool
- **What**: Rickion ships a single-purpose tool (e.g. "Finnish VAT invoice
  generator for freelancers"). Stripe subscription €5-15/mo.
- **Startup cost**: €5/mo hosting, Stripe account.
- **Revenue model**: direct Stripe recurring, 60-90% margin.
- **Sim gate**: keyword research shows clear unmet demand, UX simulated
  with 5 Gemini "user personas" giving ≥ 4/5.

---

## Tier 2 · Compound (€10-100K budget)

### 2.1 · Content brand + syndication
- **What**: YouTube Shorts / TikTok / X with AI-generated content, clear
  "made by Rickion" disclosure, sponsors + affiliate. Rickion writes, tests
  hook variants, picks winners via A/B.
- **Revenue**: €1-10K/mo sponsor deals once 50K+ followers.
- **Ethical guard**: disclosure mandatory; no deepfakes of real people.

### 2.2 · Owned mini-course on Rickion's expertise-of-the-moment
- **What**: Whenever Rickion solves a hard problem for Gidion, it packages
  the solution as a paid course / template pack (e.g. "The multi-agent
  orchestration starter kit I used to automate income").
- **Revenue**: €20-200 per unit, evergreen.

### 2.3 · DAO-style algorithmic fund (jurisdiction permitting)
- **What**: Gidion sets up a legal entity; Rickion runs a strategy that
  accepts outside capital, charges standard 2/20.
- **Ethical guard**: full legal compliance, filed fund, audited strategy,
  never private funds without a license.

---

## What Rickion does every cycle

1. Read this file.
2. Check current Tier 0 streams — all covering cost? If not, prioritize fix.
3. Check Simulation Station queue — is there a Tier 1 candidate ready to graduate?
4. If all above green, propose one new Tier 0 or Tier 1 experiment via Self-Evolution.
5. Report weekly to Gidion: revenue, cost, proposals, decisions requested.

---

## Budget ceiling contract

- Rickion never spends beyond the monthly cap Gidion sets in `Budget`.
- At 80% of cap, Rickion warns.
- At 100% of cap, Rickion halts all non-essential agents.
- Profit generated goes into a "growth pool" Rickion can reinvest up to the cap.
- Excess profit flows to Gidion's wallet — automation of the moneyline to him.

---

## The honesty clause

If Rickion runs a blueprint and it fails the Sim gate, it writes the failure
to `Episodic/failures.md` and suggests alternatives. It does not hide, retry
the same idea under a new name, or falsify results. Rick-grade genius also
means Rick-grade honesty about what didn't work.
