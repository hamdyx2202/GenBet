# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *

import json
import typing


class GenBet(gl.Contract):
    question: str
    option_a: str
    option_b: str
    resolution_url: str
    has_resolved: bool
    outcome: str
    confidence: str

    def __init__(self, question: str, option_a: str, option_b: str, resolution_url: str):
        self.question = question
        self.option_a = option_a
        self.option_b = option_b
        self.resolution_url = resolution_url
        self.has_resolved = False
        self.outcome = ""
        self.confidence = ""

    @gl.public.write
    def resolve(self) -> typing.Any:

        if self.has_resolved:
            raise gl.vm.UserError("Already resolved")

        market_url = self.resolution_url
        question = self.question
        opt_a = self.option_a
        opt_b = self.option_b

        def fetch_and_resolve() -> typing.Any:
            web_data = gl.nondet.web.render(market_url, mode="text")
            print(web_data)

            task = f"""
Based on the following web page data, determine the outcome of this prediction:

Question: {question}
Option A: {opt_a}
Option B: {opt_b}

Web page content:
{web_data}
End of web page data.

If the data does not clearly indicate an outcome, respond with winner as -1.

Respond with the following JSON format:
{{
    "outcome": str, // The exact text of the winning option, either "{opt_a}" or "{opt_b}", or "undetermined"
    "winner": int, // 1 for Option A, 2 for Option B, 0 for draw, -1 if not yet determined
    "confidence": str // "high", "medium", or "low"
}}
It is mandatory that you respond only using the JSON format above,
nothing else. Don't include any other words or characters,
your output must be only JSON without any formatting prefix or suffix.
This result should be perfectly parsable by a JSON parser without errors.
            """
            result = (
                gl.nondet.exec_prompt(task).replace("```json", "").replace("```", "")
            )
            print(result)
            return json.loads(result)

        result_json = gl.eq_principle.strict_eq(fetch_and_resolve)

        if result_json["winner"] > -1:
            self.has_resolved = True
            self.outcome = result_json["outcome"]
            self.confidence = result_json["confidence"]

        return result_json

    @gl.public.view
    def get_resolution_data(self) -> dict[str, typing.Any]:
        return {
            "question": self.question,
            "option_a": self.option_a,
            "option_b": self.option_b,
            "outcome": self.outcome,
            "confidence": self.confidence,
            "has_resolved": self.has_resolved,
        }
