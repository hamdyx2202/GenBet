# GenBet - AI Prediction Market on GenLayer

**Bet on real-world outcomes. AI resolves the truth.**

> The first prediction market where outcomes are resolved by AI consensus — not centralized oracles, not manual reporting, but Intelligent Contracts that read the real world.

## What It Does

GenBet lets users create prediction markets on any real-world event. When the event concludes, an Intelligent Contract:

1. **Fetches** real-world data from the source URL
2. **Analyzes** it using an LLM to determine the outcome
3. **Reaches consensus** via Optimistic Democracy (multiple validators must agree)
4. **Distributes** winnings to correct bettors automatically

No oracle feeds. No manual resolution. No trust assumptions. Just AI reading the web and validators agreeing on truth.

## How It Works

```
User creates market: "Will BTC hit $100K by April?"
    → Option A: "Yes"  |  Option B: "No"
    → Resolution URL: coinmarketcap.com/bitcoin

Users place bets with GEN tokens
    → 5 users bet "Yes" (total: 500 GEN)
    → 3 users bet "No" (total: 300 GEN)

When event concludes → Anyone calls resolve_market()
    → Intelligent Contract fetches coinmarketcap.com
    → AI extracts: "BTC price: $102,450" → Outcome: "Yes"
    → Validators verify independently (Equivalence Principle)
    → All agree → Market resolved

Winners claim proportional share of total pool (800 GEN)
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    GenBet                             │
├─────────────────┬───────────────────────────────────┤
│  Intelligent    │  GenLayer Blockchain               │
│  Contract       │                                    │
│  (Python)       │  • Optimistic Democracy consensus  │
│                 │  • AI validators with LLMs          │
│  • Create       │  • Equivalence Principle            │
│    markets      │  • Proportional winner payouts       │
│  • Place bets   │                                    │
│  • AI resolve   │  Web Access:                       │
│  • Auto-payout  │  • gl.nondet.web.render()          │
│                 │  • gl.nondet.exec_prompt()          │
│                 │  • gl.eq_principle.strict_eq()      │
└─────────────────┴───────────────────────────────────┘
```

## Intelligent Contract Features

| Feature | Description |
|---------|-------------|
| **Create Markets** | Any user can create a market with a question, two options, and a resolution URL |
| **Place Bets** | Send GEN tokens to bet on your predicted outcome |
| **AI Resolution** | Contract fetches web data and uses LLM to determine outcome |
| **Consensus Verification** | Multiple validators independently verify the AI's answer |
| **Auto-Payout** | Winners receive proportional share of the total pool |
| **Points Tracking** | Track user winnings with `get_user_points()` |
| **Bet Accumulation** | Users can add to existing bets on same option |
| **Platform Stats** | Total markets, volume, and resolved count |

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- GenLayer CLI (`npm install -g genlayer`)

### Setup
```bash
git clone https://github.com/hamdyx2202/GenBet.git
cd GenBet
pip install -r requirements.txt
npm install
```

### Deploy
```bash
genlayer network          # Select testnet-bradbury
genlayer deploy           # Deploy the Intelligent Contract
```

### Test in GenLayer Studio
Visit [studio.genlayer.com](https://studio.genlayer.com/) and paste the contract code to test interactively.

## Contract Methods

| Method | Type | Description |
|--------|------|-------------|
| `create_market(question, option_a, option_b, url)` | write | Create a new prediction market |
| `place_bet(market_id, option)` | write.payable | Bet GEN tokens on an option |
| `resolve_market(market_id)` | write | AI fetches data and resolves outcome |
| `claim_winnings(market_id)` | write | Winners withdraw their share |
| `get_market(market_id)` | view | Get market details |
| `get_user_bet(market_id, user)` | view | Get user's bet on a market |
| `get_user_points(user)` | view | Get user's total winnings |
| `get_stats()` | view | Platform statistics |
| `get_market_count()` | view | Total number of markets |

## AI Resolution Flow (The GenLayer-Unique Part)

```python
def fetch_and_resolve():
    # 1. Fetch real-world data
    web_data = gl.nondet.web.render(resolution_url, mode="text")

    # 2. AI determines the outcome
    result = gl.nondet.exec_prompt(
        f"Question: {question}\nData: {web_data}\nWhich option won?"
    )

    # 3. Return ONLY deterministic outcome for consensus
    return json.dumps({"outcome": result.strip()}, sort_keys=True)

# 4. Validators must ALL agree (Equivalence Principle)
outcome = gl.eq_principle.strict_eq(fetch_and_resolve)
```

This is impossible on Ethereum or Solana — only GenLayer's Intelligent Contracts can natively access the web and use AI for consensus.

## Use Cases

- **Sports:** "Will Real Madrid win El Clasico?" → resolves from BBC Sport
- **Crypto:** "Will BTC hit $100K by April?" → resolves from CoinMarketCap
- **Politics:** "Will candidate X win the election?" → resolves from news sources
- **Weather:** "Will it rain in Cairo tomorrow?" → resolves from weather API
- **Tech:** "Will Apple announce a new product at WWDC?" → resolves from tech news

## Project Structure

```
GenBet/
├── contracts/
│   └── prediction_market.py    # Intelligent Contract (Python)
├── deploy/
│   └── deployScript.ts         # Deployment script
├── requirements.txt
├── package.json
├── README.md
└── LICENSE
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Smart Contract | GenLayer Intelligent Contract (Python) |
| AI | LLMs via gl.nondet.exec_prompt() |
| Web Access | gl.nondet.web.render() |
| Consensus | Optimistic Democracy + Equivalence Principle |
| Deployment | GenLayer CLI + Testnet Bradbury |

## Revenue Potential

GenLayer's dev fee model enables contracts to earn **up to 20% of transaction fees** generated on mainnet. Top hackathon projects get priority mainnet deployment and first access to this revenue model.

## Built For

[GenLayer Testnet Bradbury Hackathon](https://dorahacks.io/hackathon/genlayer-testnet-bradbury) — Prediction Markets & P2P Betting Track

## License

MIT
