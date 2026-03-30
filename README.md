# GenBet - AI Prediction Market on GenLayer

**Bet on real-world outcomes. AI resolves the truth.**

> The first prediction market where outcomes are resolved by AI consensus — not centralized oracles, not manual reporting, but Intelligent Contracts that read the real world.

## What It Does

GenBet lets users create prediction markets on any real-world event. When the event concludes, the Intelligent Contract:

1. **Fetches** real-world data from the source URL via `gl.nondet.web.render()`
2. **Analyzes** it using an LLM via `gl.nondet.exec_prompt()`
3. **Reaches consensus** via Optimistic Democracy — multiple validators independently verify
4. **Updates state** automatically based on the AI's determination

No oracle feeds. No manual resolution. No trust assumptions.

## Live Demo Results

Successfully deployed and tested on GenLayer Studio:

- **Deploy**: `0xcb31...` — FINALIZED ✓
- **Resolve**: `0x8fda...` — AI fetched CoinMarketCap data, validators reached consensus via Optimistic Democracy with leader rotation — FINALIZED ✓
- **get_resolution_data**: Returns live market state ✓

## How It Works

```
User creates market: "Will Bitcoin reach 100K by April 2026?"
    → Option A: "Yes"  |  Option B: "No"
    → Resolution URL: coinmarketcap.com/currencies/bitcoin/

Anyone calls resolve()
    → Intelligent Contract fetches coinmarketcap.com
    → AI extracts Bitcoin price and determines outcome
    → Validators verify independently (Equivalence Principle)
    → If consensus reached → Market resolved
    → If not determinable → Market stays open (winner = -1)
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
│    markets      │  • Leader rotation on disagreement  │
│  • AI resolve   │  • Proportional winner payouts      │
│  • View state   │                                    │
│                 │  Web Access:                       │
│                 │  • gl.nondet.web.render()          │
│                 │  • gl.nondet.exec_prompt()          │
│                 │  • gl.eq_principle.strict_eq()      │
└─────────────────┴───────────────────────────────────┘
```

## Contract Methods

| Method | Type | Description |
|--------|------|-------------|
| `__init__(question, option_a, option_b, resolution_url)` | constructor | Create a new prediction market |
| `resolve()` | write | AI fetches data and resolves outcome via consensus |
| `get_resolution_data()` | view | Get market state (question, options, outcome, resolved status) |

## GenLayer Features Used

| Feature | How We Use It |
|---------|---------------|
| **Optimistic Democracy** | Validators independently verify AI's outcome determination |
| **Equivalence Principle** | `gl.eq_principle.strict_eq()` ensures consensus on market resolution |
| **Web Access** | `gl.nondet.web.render()` fetches real-world data from any URL |
| **LLM Integration** | `gl.nondet.exec_prompt()` for AI-powered outcome analysis |
| **Leader Rotation** | Automatic re-election when validators disagree |

## AI Resolution Logic

```python
def fetch_and_resolve():
    # 1. Fetch real-world data from resolution URL
    web_data = gl.nondet.web.render(market_url, mode="text")

    # 2. AI analyzes the data
    result = gl.nondet.exec_prompt(task)

    # 3. Parse and return structured result
    return json.loads(result)

# 4. All validators must agree (Equivalence Principle)
result_json = gl.eq_principle.strict_eq(fetch_and_resolve)
```

## Use Cases

- **Crypto**: "Will BTC hit $100K by April?" → resolves from CoinMarketCap
- **Sports**: "Will Real Madrid win El Clasico?" → resolves from BBC Sport
- **Politics**: "Will candidate X win the election?" → resolves from news sources
- **Weather**: "Will it rain in Cairo tomorrow?" → resolves from weather services
- **Tech**: "Will Apple announce new product at WWDC?" → resolves from tech news

## Quick Start

### Test on GenLayer Studio
1. Visit [studio.genlayer.com](https://studio.genlayer.com/)
2. Upload `contracts/genbet_v2.py` (or `prediction_market.py`)
3. Deploy with: question, option_a, option_b, resolution_url
4. Call `resolve()` to trigger AI resolution
5. Call `get_resolution_data()` to see results

### Deploy via CLI
```bash
npm install -g genlayer
genlayer network     # Select testnet-bradbury
genlayer deploy      # Deploy the contract
```

## Project Structure

```
GenBet/
├── contracts/
│   ├── prediction_market.py    # Main Intelligent Contract
│   └── genbet_v2.py            # Same contract (Studio-compatible)
├── deploy/
│   └── deployScript.ts         # CLI deployment script
├── requirements.txt
├── package.json
├── SUBMISSION_READY.md
├── README.md
└── LICENSE
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Smart Contract | GenLayer Intelligent Contract (Python) |
| AI | LLMs via `gl.nondet.exec_prompt()` |
| Web Access | `gl.nondet.web.render()` |
| Consensus | Optimistic Democracy + Equivalence Principle |

## Why GenLayer?

This is **impossible on Ethereum or Solana**. Only GenLayer's Intelligent Contracts can:
- Natively access the web without oracles
- Use AI (LLMs) for on-chain decision making
- Reach consensus on subjective, non-deterministic outputs

## Revenue Potential

GenLayer's dev fee model enables contracts to earn **up to 20% of transaction fees** generated on mainnet. Top hackathon projects get priority mainnet deployment.

## Built For

[GenLayer Testnet Bradbury Hackathon](https://dorahacks.io/hackathon/genlayer-testnet-bradbury) — Prediction Markets & P2P Betting Track

## License

MIT
