# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

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
    resolved: bool
    outcome: str


class GenBet(gl.Contract):
    market_count: u256
    markets: TreeMap[str, Market]
    total_resolved: u256

    def __init__(self):
        self.market_count = u256(0)
        self.total_resolved = u256(0)

    @gl.public.write
    def create_market(self, question: str, option_a: str, option_b: str, resolution_url: str) -> str:
        market_id = "market_" + str(int(self.market_count))
        self.market_count = u256(int(self.market_count) + 1)
        self.markets[market_id] = Market(
            id=market_id,
            question=question,
            resolution_url=resolution_url,
            creator=str(gl.message.sender),
            option_a=option_a,
            option_b=option_b,
            resolved=False,
            outcome="",
        )
        return market_id

    @gl.public.write
    def resolve_market(self, market_id: str) -> str:
        market = gl.storage.copy_to_memory(self.markets[market_id])
        if market.resolved:
            raise Exception("Already resolved")

        def fetch_and_resolve():
            web_data = gl.nondet.web.render(market.resolution_url, mode="text")
            prompt = (
                f"Based on this web data, determine the outcome.

"
                f"Question: {market.question}
"
                f"Option A: {market.option_a}
"
                f"Option B: {market.option_b}

"
                f"Web data:
{web_data[:3000]}

"
                f"Respond with ONLY the exact text of the winning option. "
                f"Either "{market.option_a}" or "{market.option_b}". Nothing else."
            )
            result = gl.nondet.exec_prompt(prompt)
            outcome = result.strip().strip('"').strip("''")
            if market.option_a.lower() in outcome.lower():
                outcome = market.option_a
            elif market.option_b.lower() in outcome.lower():
                outcome = market.option_b
            return json.dumps({"outcome": outcome}, sort_keys=True)

        result_str = gl.eq_principle.strict_eq(fetch_and_resolve)
        result = json.loads(result_str)
        winning_option = result["outcome"]
        self.markets[market_id].resolved = True
        self.markets[market_id].outcome = winning_option
        self.total_resolved = u256(int(self.total_resolved) + 1)
        return result_str

    @gl.public.view
    def get_market(self, market_id: str) -> dict:
        m = self.markets[market_id]
        return {
            "id": m.id,
            "question": m.question,
            "option_a": m.option_a,
            "option_b": m.option_b,
            "resolved": m.resolved,
            "outcome": m.outcome,
        }

    @gl.public.view
    def get_stats(self) -> dict:
        return {
            "total_markets": str(int(self.market_count)),
            "total_resolved": str(int(self.total_resolved)),
        }

    @gl.public.view
    def get_market_count(self) -> bigint:
        return int(self.market_count)
