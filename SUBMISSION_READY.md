# DoraHacks Submission - GenLayer Testnet Bradbury Hackathon

## Project Name
GenBet

## Track
Prediction Markets & P2P Betting

## GitHub Link
https://github.com/hamdyx2202/GenBet

## Demo Video
[PASTE YOUTUBE LINK AFTER RECORDING]

## Short Description (for BUIDL vision - max 256 chars)
AI prediction oracle on GenLayer where Intelligent Contracts resolve real-world outcomes by fetching web data and reaching AI consensus via Optimistic Democracy and Equivalence Principle.

## Full Description

### GenBet - AI Prediction Market

GenBet is an AI-powered prediction resolution system built on GenLayer where real-world outcomes are determined by AI consensus — not centralized oracles or manual reporting.

### How It Works
1. Users create prediction markets on any real-world event with a question, two options, and a resolution URL
2. When the event concludes, anyone triggers resolution
3. The Intelligent Contract fetches real-world data from the URL
4. AI analyzes the data to determine the outcome
5. Multiple validators independently verify (Equivalence Principle)
6. Market state updates with the resolved outcome

### GenLayer-Specific Features
- **Optimistic Democracy**: Validators use LLMs to reach consensus on market outcomes
- **Equivalence Principle**: `gl.eq_principle.strict_eq()` ensures all validators agree
- **Web Access**: `gl.nondet.web.render()` fetches real-world data natively
- **LLM Integration**: `gl.nondet.exec_prompt()` for AI-powered outcome determination
- **Python Contract**: Clean, readable Intelligent Contract

### Why GenLayer?
This is impossible on Ethereum or Solana. Only GenLayer's Intelligent Contracts can natively access the web and use AI for consensus — eliminating the need for external oracles entirely.

## Tags
AI, Blockchain, Prediction Markets, P2P Betting, GenLayer, Web3
