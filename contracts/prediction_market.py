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
    creator: str
    option_a: str
    option_b: str
    total_a: u256
    total_b: u256
    resolved: bool
    outcome: str


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
    bets: TreeMap[str, TreeMap[str, Bet]]
    user_points: TreeMap[str, u256]
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
            creator=str(gl.message.sender),
            option_a=option_a,
            option_b=option_b,
            total_a=u256(0),
            total_b=u256(0),
            resolved=False,
            outcome="",
        )

        return market_id

    @gl.public.write.payable
    def place_bet(self, market_id: str, option: str) -> None:
        """Place a bet on a market option. Send GEN tokens with this call."""
        if self.markets[market_id].resolved:
            raise Exception("Market already resolved")

        option_a = self.markets[market_id].option_a
        option_b = self.markets[market_id].option_b

        if option != option_a and option != option_b:
            raise Exception("Invalid option. Choose: " + option_a + " or " + option_b)

        amount = gl.message.value
        if int(amount) == 0:
            raise Exception("Must send GEN tokens to place bet")

        # Update market totals DIRECTLY on storage (not local copy)
        if option == option_a:
            current = int(self.markets[market_id].total_a)
            self.markets[market_id].total_a = u256(current + int(amount))
        else:
            current = int(self.markets[market_id].total_b)
            self.markets[market_id].total_b = u256(current + int(amount))

        self.total_volume = u256(int(self.total_volume) + int(amount))

        # Record bet - accumulate if user already bet on same option
        user_hex = str(gl.message.sender)

        existing_amount = u256(0)
        try:
            existing_bet = self.bets[market_id][user_hex]
            if existing_bet.option == option:
                existing_amount = existing_bet.amount
            else:
                raise Exception("Cannot bet on both options. You already bet on: " + existing_bet.option)
        except (KeyError, Exception) as e:
            if "Cannot bet on both" in str(e):
                raise

        self.bets[market_id][user_hex] = Bet(
            market_id=market_id,
            option=option,
            amount=u256(int(existing_amount) + int(amount)),
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

        # Verify market has bets
        total = int(market.total_a) + int(market.total_b)
        if total == 0:
            raise Exception("No bets placed yet")

        # AI fetches and analyzes real-world data
        def fetch_and_resolve():
            web_data = gl.nondet.web.render(market.resolution_url, mode="text")

            prompt = (
                f"Based on the following web data, determine the outcome of this prediction.\n\n"
                f"Question: {market.question}\n"
                f"Option A: {market.option_a}\n"
                f"Option B: {market.option_b}\n\n"
                f"Web data:\n{web_data[:3000]}\n\n"
                f"You MUST respond with ONLY the exact text of the winning option. "
                f"Your response must be exactly one of these two strings:\n"
                f'"{market.option_a}" or "{market.option_b}"\n\n'
                f"Do not add any other text. Just the winning option."
            )

            result = gl.nondet.exec_prompt(prompt)
            # Clean the response to match exactly one option
            outcome = result.strip().strip('"').strip("'")

            # Force match to one of the options
            if market.option_a.lower() in outcome.lower():
                outcome = market.option_a
            elif market.option_b.lower() in outcome.lower():
                outcome = market.option_b

            # Return ONLY the deterministic outcome for strict_eq consensus
            return json.dumps({"outcome": outcome}, sort_keys=True)

        # Equivalence Principle: all validators must agree on the outcome
        result_str = gl.eq_principle.strict_eq(fetch_and_resolve)
        result = json.loads(result_str)

        winning_option = result["outcome"]

        # Validate the outcome matches one of the options
        if winning_option != market.option_a and winning_option != market.option_b:
            raise Exception("AI could not determine a valid outcome: " + winning_option)

        # Update market state
        self.markets[market_id].resolved = True
        self.markets[market_id].outcome = winning_option
        self.total_resolved = u256(int(self.total_resolved) + 1)

        return result_str

    @gl.public.write
    def claim_winnings(self, market_id: str) -> None:
        """Claim winnings from a resolved market."""
        if not self.markets[market_id].resolved:
            raise Exception("Market not resolved yet")

        user_hex = str(gl.message.sender)

        # Check bet exists
        try:
            bet = self.bets[market_id][user_hex]
        except KeyError:
            raise Exception("You have no bet on this market")

        if bet.claimed:
            raise Exception("Already claimed")

        market_outcome = self.markets[market_id].outcome
        if bet.option != market_outcome:
            raise Exception("You did not bet on the winning option")

        # Calculate winnings: winner gets proportional share of total pool
        total_pool = int(self.markets[market_id].total_a) + int(self.markets[market_id].total_b)
        if market_outcome == self.markets[market_id].option_a:
            winning_pool = int(self.markets[market_id].total_a)
        else:
            winning_pool = int(self.markets[market_id].total_b)

        if winning_pool == 0:
            raise Exception("No bets on winning side")

        winnings = (int(bet.amount) * total_pool) // winning_pool

        # Mark as claimed
        self.bets[market_id][user_hex].claimed = True

        # Track points
        current_points = u256(0)
        try:
            current_points = self.user_points[user_hex]
        except KeyError:
            pass
        self.user_points[user_hex] = u256(int(current_points) + winnings)

        # Transfer winnings
        gl.transfer(gl.message.sender, u256(winnings))

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
    def get_user_bet(self, market_id: str, user_address: str) -> dict:
        """Get a user's bet on a specific market."""
        try:
            bet = self.bets[market_id][user_address]
            return {
                "option": bet.option,
                "amount": str(int(bet.amount)),
                "claimed": bet.claimed,
            }
        except KeyError:
            return {"option": "", "amount": "0", "claimed": False}

    @gl.public.view
    def get_user_points(self, user_address: str) -> str:
        """Get total points/winnings for a user."""
        try:
            return str(int(self.user_points[user_address]))
        except KeyError:
            return "0"

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
