"""
GenBet - AI Prediction Market on GenLayer

An Intelligent Contract that lets users create prediction markets,
place bets, and have AI resolve outcomes by analyzing real-world data.

Uses:
- gl.nondet.web.render() to fetch real-world results
- gl.nondet.exec_prompt() for AI analysis
- gl.eq_principle.strict_eq() for consensus on outcomes
- Optimistic Democracy for fair resolution
"""

from genlayer import *
import json


@allow_storage
@dataclass
class Market:
    id: str
    question: str
    resolution_url: str
    creator: Address
    option_a: str
    option_b: str
    total_a: u256
    total_b: u256
    resolved: bool
    outcome: str
    created_at: str


@allow_storage
@dataclass
class Bet:
    market_id: str
    option: str
    amount: u256
    claimed: bool


class GenBet(gl.Contract):
    """
    AI-powered prediction market where outcomes are resolved
    by Intelligent Contracts fetching and analyzing real-world data.
    """

    market_count: u256
    markets: TreeMap[str, Market]
    bets: TreeMap[str, TreeMap[str, Bet]]  # market_id -> user_hex -> Bet
    user_points: TreeMap[str, u256]  # user_hex -> total points won
    total_volume: u256
    total_resolved: u256

    def __init__(self):
        self.market_count = u256(0)
        self.total_volume = u256(0)
        self.total_resolved = u256(0)

    @gl.public.write
    def create_market(
        self,
        question: str,
        option_a: str,
        option_b: str,
        resolution_url: str,
    ) -> str:
        """Create a new prediction market with a question and two options."""
        market_id = "market_" + str(int(self.market_count))
        self.market_count = u256(int(self.market_count) + 1)

        self.markets[market_id] = Market(
            id=market_id,
            question=question,
            resolution_url=resolution_url,
            creator=gl.message.sender,
            option_a=option_a,
            option_b=option_b,
            total_a=u256(0),
            total_b=u256(0),
            resolved=False,
            outcome="",
            created_at="",
        )

        return market_id

    @gl.public.write.payable
    def place_bet(self, market_id: str, option: str) -> None:
        """Place a bet on a market option. Send GEN tokens with this call."""
        market = self.markets[market_id]

        if market.resolved:
            raise Exception("Market already resolved")

        if option != market.option_a and option != market.option_b:
            raise Exception("Invalid option. Choose: " + market.option_a + " or " + market.option_b)

        amount = gl.message.value
        if int(amount) == 0:
            raise Exception("Must send GEN tokens to place bet")

        # Update market totals
        if option == market.option_a:
            market.total_a = u256(int(market.total_a) + int(amount))
        else:
            market.total_b = u256(int(market.total_b) + int(amount))

        self.total_volume = u256(int(self.total_volume) + int(amount))

        # Record bet
        user_hex = str(gl.message.sender)
        if market_id not in self.bets:
            self.bets[market_id] = TreeMap[str, Bet]()

        self.bets[market_id][user_hex] = Bet(
            market_id=market_id,
            option=option,
            amount=amount,
            claimed=False,
        )

    @gl.public.write
    def resolve_market(self, market_id: str) -> str:
        """
        AI resolves the market by fetching real-world data and analyzing it.
        Uses Equivalence Principle for consensus among validators.
        """
        market = gl.storage.copy_to_memory(self.markets[market_id])

        if market.resolved:
            raise Exception("Already resolved")

        # AI fetches and analyzes real-world data
        def fetch_and_resolve():
            web_data = gl.nondet.web.render(market.resolution_url, mode="text")

            prompt = (
                f"Based on the following web data, determine the outcome of this prediction:\n\n"
                f"Question: {market.question}\n"
                f"Option A: {market.option_a}\n"
                f"Option B: {market.option_b}\n\n"
                f"Web data:\n{web_data[:3000]}\n\n"
                f"Respond ONLY with a JSON object:\n"
                f'{{"outcome": "<exact text of winning option>", "confidence": <0.0-1.0>, "reasoning": "<brief explanation>"}}'
            )

            result = gl.nondet.exec_prompt(prompt, response_format="json")
            # Normalize: only keep outcome for consensus
            outcome = result.get("outcome", "")
            confidence = result.get("confidence", 0)
            reasoning = result.get("reasoning", "")

            return json.dumps({
                "outcome": outcome,
                "confidence": confidence,
                "reasoning": reasoning
            }, sort_keys=True)

        # Equivalence Principle: all validators must agree on the outcome
        result_str = gl.eq_principle.strict_eq(fetch_and_resolve)
        result = json.loads(result_str)

        winning_option = result["outcome"]

        # Validate the outcome matches one of the options
        if winning_option != market.option_a and winning_option != market.option_b:
            raise Exception("AI could not determine a valid outcome")

        # Update market state
        self.markets[market_id].resolved = True
        self.markets[market_id].outcome = winning_option
        self.total_resolved = u256(int(self.total_resolved) + 1)

        return result_str

    @gl.public.write
    def claim_winnings(self, market_id: str) -> None:
        """Claim winnings from a resolved market."""
        market = self.markets[market_id]

        if not market.resolved:
            raise Exception("Market not resolved yet")

        user_hex = str(gl.message.sender)
        bet = self.bets[market_id][user_hex]

        if bet.claimed:
            raise Exception("Already claimed")

        if bet.option != market.outcome:
            raise Exception("You did not bet on the winning option")

        # Calculate winnings: winner gets proportional share of total pool
        total_pool = int(market.total_a) + int(market.total_b)
        winning_pool = int(market.total_a) if market.outcome == market.option_a else int(market.total_b)

        if winning_pool == 0:
            raise Exception("No bets on winning side")

        winnings = (int(bet.amount) * total_pool) // winning_pool

        # Mark as claimed
        self.bets[market_id][user_hex].claimed = True

        # Track points
        if user_hex not in self.user_points:
            self.user_points[user_hex] = u256(0)
        self.user_points[user_hex] = u256(int(self.user_points[user_hex]) + winnings)

        # Transfer winnings
        gl.message.sender.transfer(u256(winnings))

    @gl.public.view
    def get_market(self, market_id: str) -> dict:
        """Get details of a specific market."""
        m = self.markets[market_id]
        return {
            "id": m.id,
            "question": m.question,
            "option_a": m.option_a,
            "option_b": m.option_b,
            "total_a": str(int(m.total_a)),
            "total_b": str(int(m.total_b)),
            "resolved": m.resolved,
            "outcome": m.outcome,
            "resolution_url": m.resolution_url,
        }

    @gl.public.view
    def get_stats(self) -> dict:
        """Get platform statistics."""
        return {
            "total_markets": str(int(self.market_count)),
            "total_volume": str(int(self.total_volume)),
            "total_resolved": str(int(self.total_resolved)),
        }

    @gl.public.view
    def get_market_count(self) -> int:
        return int(self.market_count)
