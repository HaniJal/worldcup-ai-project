"""
Guardrails for the costly AI endpoints (/v1/agent/ask, /v1/rag/ask):

1. A lifetime cap on requests per (IP, endpoint) pair - not a rolling
   window, a permanent counter, so once a visitor uses their allotted
   requests on an endpoint they cannot use it again from that IP.
2. A hard global spend ceiling, tracked in the DB from real token usage
   returned by the Anthropic API (and a fixed per-call estimate for
   Tavily). Once the running total crosses the ceiling, both endpoints
   stop making paid calls entirely.
3. A permanent cache of (endpoint, question) -> response, so a repeated
   question is served for free and doesn't count against the asker's
   rate limit or the spend total.

Both checks happen before any paid API call is made, so a blocked request
never actually reaches Claude or Tavily.
"""

import json
import re

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.settings import settings
from src.usage.models import ApiSpendLog, IpRequestCount, ResponseCache

# Anthropic Haiku 4.5 pricing (per token), confirmed Sep 2026.
ANTHROPIC_INPUT_COST_PER_TOKEN = 1.00 / 1_000_000
ANTHROPIC_OUTPUT_COST_PER_TOKEN = 5.00 / 1_000_000

# Tavily basic search, flat estimate per call (pay-as-you-go rate).
TAVILY_COST_PER_SEARCH = 0.008


class RateLimitExceeded(Exception):
    pass


class BudgetExceeded(Exception):
    pass


async def get_total_spend(db: AsyncSession) -> float:
    result = await db.execute(select(func.coalesce(func.sum(ApiSpendLog.estimated_cost_usd), 0.0)))
    return float(result.scalar_one())


async def check_budget(db: AsyncSession) -> None:
    total = await get_total_spend(db)
    if total >= settings.MAX_API_SPEND_USD:
        raise BudgetExceeded(
            f"Demo budget of ${settings.MAX_API_SPEND_USD:.2f} has been reached. "
            "This endpoint is temporarily disabled - please check back later."
        )


async def check_and_increment_ip_limit(db: AsyncSession, ip_address: str, endpoint: str) -> None:
    """
    Raises RateLimitExceeded if this IP has already used up its lifetime
    allotment of requests on this endpoint. Otherwise increments the count.
    Call this BEFORE making any paid API call.
    """
    result = await db.execute(
        select(IpRequestCount).where(
            IpRequestCount.ip_address == ip_address, IpRequestCount.endpoint == endpoint
        )
    )
    record = result.scalar_one_or_none()

    current_count = record.request_count if record else 0
    if current_count >= settings.MAX_REQUESTS_PER_IP:
        raise RateLimitExceeded(
            f"You've reached the limit of {settings.MAX_REQUESTS_PER_IP} requests "
            f"for this demo endpoint. Thanks for trying it out!"
        )

    if record:
        record.request_count += 1
    else:
        db.add(IpRequestCount(ip_address=ip_address, endpoint=endpoint, request_count=1))
    await db.flush()


async def record_anthropic_spend(db: AsyncSession, endpoint: str, input_tokens: int, output_tokens: int) -> None:
    cost = input_tokens * ANTHROPIC_INPUT_COST_PER_TOKEN + output_tokens * ANTHROPIC_OUTPUT_COST_PER_TOKEN
    db.add(ApiSpendLog(endpoint=endpoint, provider="anthropic", estimated_cost_usd=cost))
    await db.flush()


async def record_tavily_spend(db: AsyncSession, endpoint: str, num_searches: int = 1) -> None:
    cost = num_searches * TAVILY_COST_PER_SEARCH
    db.add(ApiSpendLog(endpoint=endpoint, provider="tavily", estimated_cost_usd=cost))
    await db.flush()


def normalize_question(question: str) -> str:
    """
    Collapse trivial variations (case, extra whitespace, trailing
    punctuation) so 'Who won?' and 'who won' hit the same cache entry.
    """
    text = question.strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[?!.]+$", "", text)
    return text[:500]


async def get_cached_response(db: AsyncSession, endpoint: str, question: str) -> dict | None:
    key = normalize_question(question)
    result = await db.execute(
        select(ResponseCache).where(
            ResponseCache.endpoint == endpoint, ResponseCache.question_key == key
        )
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None
    return json.loads(record.response_json)


async def store_cached_response(db: AsyncSession, endpoint: str, question: str, response: dict) -> None:
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    key = normalize_question(question)
    stmt = (
        pg_insert(ResponseCache)
        .values(endpoint=endpoint, question_key=key, response_json=json.dumps(response, default=str))
        .on_conflict_do_nothing(index_elements=["endpoint", "question_key"])
    )
    await db.execute(stmt)
    await db.flush()
