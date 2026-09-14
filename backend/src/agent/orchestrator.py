"""
The agent loop: give Claude a question and a set of tools, let it decide
which to call (possibly several, possibly in sequence), execute them, feed
results back, and repeat until Claude has enough to give a final answer.

This is the actual "routing" logic from the project's Layer 3 - instead of
hand-written if/else rules deciding "is this a SQL question or a RAG
question", Claude reads the tool descriptions and the question and decides
for itself, the same way it would with any tool-use API call.
"""

import asyncio
import json
from dataclasses import dataclass, field

from anthropic import Anthropic
from sqlalchemy.ext.asyncio import AsyncSession

from src.agent import db_tools
from src.agent.tools import TOOL_DEFINITIONS
from src.agent.web_tools import web_search
from src.rag.service import retrieve as rag_retrieve
from src.settings import settings

MAX_TOOL_ITERATIONS = 5

SYSTEM_PROMPT = """You are an assistant for the FIFA World Cup 2026. You have \
access to tools that query a structured database, search a knowledge base of \
match/team/player summaries, and search the live web. Choose whichever \
tool(s) best answer the user's question - prefer the database tools for \
precise facts and statistics, the knowledge base for descriptive or \
narrative questions, and web search only for things outside the tournament \
dataset. You may call more than one tool if needed. Answer using only \
information returned by the tools; if the tools don't have an answer, say \
so plainly."""


@dataclass
class ToolCallRecord:
    name: str
    input: dict
    result: object


@dataclass
class AgentAnswer:
    answer: str
    tool_calls: list[ToolCallRecord] = field(default_factory=list)


# Tools that need a DB session (async) vs. ones that don't (sync, run in a thread)
_DB_TOOLS = {
    "get_top_scorers": db_tools.get_top_scorers,
    "get_team_record": db_tools.get_team_record,
    "get_match_result": db_tools.get_match_result,
    "get_player_stats": db_tools.get_player_stats,
    "get_tournament_champion": db_tools.get_tournament_champion,
}


async def _execute_tool(name: str, tool_input: dict, db: AsyncSession):
    if name in _DB_TOOLS:
        return await _DB_TOOLS[name](db, **tool_input)

    if name == "search_knowledge_base":
        query = tool_input["query"]
        top_k = tool_input.get("top_k", 5)
        chunks = await asyncio.to_thread(rag_retrieve, query, top_k)
        return [{"text": c.text, "score": c.score, "metadata": c.metadata} for c in chunks]

    if name == "search_web":
        return await asyncio.to_thread(web_search, tool_input["query"])

    return {"error": f"Unknown tool: {name}"}


def _default_json(obj):
    """Fallback for json.dumps on things like dates that aren't natively serializable."""
    return str(obj)


async def run_agent(question: str, db: AsyncSession) -> AgentAnswer:
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    messages = [{"role": "user", "content": question}]
    tool_calls: list[ToolCallRecord] = []

    for _ in range(MAX_TOOL_ITERATIONS):
        response = await asyncio.to_thread(
            client.messages.create,
            model=settings.ANTHROPIC_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            final_text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            return AgentAnswer(answer=final_text, tool_calls=tool_calls)

        tool_use_blocks = [block for block in response.content if block.type == "tool_use"]
        tool_result_content = []
        for block in tool_use_blocks:
            result = await _execute_tool(block.name, block.input, db)
            tool_calls.append(ToolCallRecord(name=block.name, input=block.input, result=result))
            tool_result_content.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, default=_default_json),
                }
            )

        messages.append({"role": "user", "content": tool_result_content})

    return AgentAnswer(
        answer="I wasn't able to reach a final answer within the allowed number of tool calls.",
        tool_calls=tool_calls,
    )
