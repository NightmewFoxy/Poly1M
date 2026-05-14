"""Use Claude with the web search tool to estimate true probability, then compute EV.

For each market we:
  1. Ask Claude to research the match/event (rosters, form, h2h, patch, news).
  2. Parse a JSON verdict block from its response (true_prob_yes + summary + confidence).
  3. Pick the side (YES or NO) where our price <= 0.80 AND EV > 0.
  4. Score the candidate so main.py can rank them.

Polymarket fee model: 2% of net winnings. For a $S stake on side at price p:
  shares = S / p
  payoff_if_win = shares * 1.0 = S/p           (gross)
  profit_if_win = S/p - S = S*(1-p)/p          (before fee)
  fee_if_win    = FEE * profit_if_win
  net_if_win    = (1 - FEE) * S*(1-p)/p
  loss          = -S
  EV($)         = true_p * net_if_win - (1 - true_p) * S
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import anthropic
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

import config
import research_cache
from logger_setup import get_logger
from polymarket_client import MarketCandidate

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# EV math
# ---------------------------------------------------------------------------


def ev_dollars(true_prob: float, price: float, stake: float = config.STAKE_USD) -> float:
    if price <= 0 or price >= 1:
        return -float("inf")
    shares = stake / price
    net_if_win = (1 - config.POLYMARKET_FEE) * (shares - stake)
    return true_prob * net_if_win - (1 - true_prob) * stake


def ev_cents_per_dollar(true_prob: float, price: float) -> float:
    """EV expressed as cents per $1 staked (e.g. +8.3 means $0.083 EV per $1)."""
    return ev_dollars(true_prob, price, stake=1.0) * 100


def potential_profit_net(price: float, stake: float = config.STAKE_USD) -> float:
    shares = stake / price
    gross_profit = shares - stake
    return (1 - config.POLYMARKET_FEE) * gross_profit


# ---------------------------------------------------------------------------
# Anthropic call
# ---------------------------------------------------------------------------


_anthropic: anthropic.Anthropic | None = None


def _client() -> anthropic.Anthropic:
    global _anthropic
    if _anthropic is None:
        _anthropic = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _anthropic


_PROMPT_TEMPLATE = """Estimate true probability of YES for this Polymarket esports market.

Question: {question}
Resolves (UTC): {end_date}
Market YES={yes_price:.2f} ({yes_implied:.0f}%), NO={no_price:.2f} ({no_implied:.0f}%)

Run 2-3 focused web searches covering: team form, head-to-head, roster/patch news, odds elsewhere. Skip a search if results would be redundant -- fewer is fine.

Return only a single fenced JSON block:

```json
{{"true_prob_yes": 0.62, "confidence": "medium", "summary": "2-3 sentences on who is favored, why, and the biggest uncertainty.", "key_facts": ["fact", "fact"]}}
```

Rules: 0.02 <= true_prob_yes <= 0.98. confidence in {{"low","medium","high"}}. If you can't find recent info, use "low" and pick a value close to {yes_implied:.0f}%."""


_JSON_BLOCK_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)


def _extract_json(text: str) -> dict[str, Any] | None:
    m = _JSON_BLOCK_RE.search(text)
    if not m:
        # Fallback: try to find the last {...} block
        last_open = text.rfind("{")
        last_close = text.rfind("}")
        if last_open == -1 or last_close == -1 or last_close < last_open:
            return None
        snippet = text[last_open : last_close + 1]
    else:
        snippet = m.group(1)
    try:
        return json.loads(snippet)
    except json.JSONDecodeError:
        return None


def _collect_text(content_blocks: list[Any]) -> str:
    parts: list[str] = []
    for b in content_blocks:
        # Anthropic SDK returns block objects with a `.type` and `.text` (for text blocks).
        btype = getattr(b, "type", None)
        if btype == "text":
            parts.append(getattr(b, "text", "") or "")
    return "\n".join(parts)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=30),
    retry=retry_if_exception_type((anthropic.APIError, anthropic.APIConnectionError)),
    reraise=True,
)
def _research_call(market: MarketCandidate) -> dict[str, Any] | None:
    prompt = _PROMPT_TEMPLATE.format(
        question=market.question,
        end_date=market.end_date_iso,
        yes_price=market.yes_price,
        no_price=market.no_price,
        yes_implied=market.yes_price * 100,
        no_implied=market.no_price * 100,
    )

    resp = _client().messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=1500,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}],
        messages=[{"role": "user", "content": prompt}],
    )
    text = _collect_text(resp.content)
    parsed = _extract_json(text)
    if not parsed:
        log.warning("No JSON verdict from Claude for: %s", market.question[:80])
        return None
    try:
        parsed["true_prob_yes"] = float(parsed["true_prob_yes"])
    except (KeyError, TypeError, ValueError):
        log.warning("Bad true_prob_yes in verdict: %s", parsed)
        return None
    if not (0.02 <= parsed["true_prob_yes"] <= 0.98):
        log.warning("true_prob_yes out of range: %s", parsed["true_prob_yes"])
        return None
    return parsed


# ---------------------------------------------------------------------------
# Public: research one market, pick a side, score it
# ---------------------------------------------------------------------------


@dataclass
class TradeIdea:
    market: MarketCandidate
    side: str              # "YES" or "NO"
    price: float           # price for that side at the moment of research
    token_id: str
    true_prob_side: float  # our probability estimate for the chosen side
    market_implied: float  # price-implied probability for the chosen side
    ev_cents: float        # EV in cents per dollar staked (after fee)
    ev_dollars: float      # EV in dollars at full STAKE_USD
    confidence: str
    summary: str
    key_facts: list[str]


def research_and_score(market: MarketCandidate) -> TradeIdea | None:
    """Run Claude + web search (or reuse a cached verdict), pick the +EV side at <= MAX_PRICE, return a TradeIdea."""
    cached = research_cache.get(market.condition_id, market.yes_price)
    if cached is not None:
        log.info("CACHE HIT: %s", market.question[:80])
        verdict = cached
    else:
        verdict = _research_call(market)
        if verdict is None:
            return None
        try:
            research_cache.put(market.condition_id, market.yes_price, verdict)
        except Exception as exc:
            log.warning("research_cache write failed: %s", exc)

    # Low-confidence verdicts mean Claude couldn't find recent info and
    # (per the prompt) was instructed to anchor to the market price.
    # Trading on these is essentially trading on noise — the EV is whatever
    # rounding error Claude introduced relative to market_implied. Skip.
    confidence = str(verdict.get("confidence", "medium")).lower()
    if confidence == "low":
        log.info(
            "Skipping low-confidence verdict: %s",
            market.question[:80],
        )
        return None

    true_p_yes = verdict["true_prob_yes"]
    true_p_no = 1.0 - true_p_yes

    # Score both sides; keep whichever is positive-EV and priced <= MAX_PRICE.
    options: list[tuple[str, float, str, float]] = [
        ("YES", market.yes_price, market.yes_token_id, true_p_yes),
        ("NO", market.no_price, market.no_token_id, true_p_no),
    ]
    best: TradeIdea | None = None
    for side, price, token_id, p_side in options:
        if price <= 0 or price > config.MAX_PRICE:
            continue
        ev_c = ev_cents_per_dollar(p_side, price)
        if ev_c <= 0:
            continue
        ev_d = ev_dollars(p_side, price)
        idea = TradeIdea(
            market=market,
            side=side,
            price=price,
            token_id=token_id,
            true_prob_side=p_side,
            market_implied=price,
            ev_cents=ev_c,
            ev_dollars=ev_d,
            confidence=str(verdict.get("confidence", "medium")),
            summary=str(verdict.get("summary", ""))[:600],
            key_facts=[str(x) for x in (verdict.get("key_facts") or [])][:5],
        )
        if best is None or idea.ev_cents > best.ev_cents:
            best = idea
    return best
