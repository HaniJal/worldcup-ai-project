"""
JSON schema definitions for every tool the agent can call. Each schema is
deliberately narrow and specific (one job per tool) rather than one generic
"query the database" dispatcher - this is what makes Claude's tool
selection reliable: a clear name and description per capability, not a
single overloaded tool it has to guess parameters for.
"""

TOOL_DEFINITIONS = [
    {
        "name": "get_top_scorers",
        "description": (
            "Get the top goal scorers in the 2026 World Cup, optionally filtered "
            "to a single team. Use for questions like 'who scored the most goals' "
            "or 'top scorers for France'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "How many players to return (default 5).",
                },
                "team_name": {
                    "type": "string",
                    "description": "Optional team name to filter by, e.g. 'France'.",
                },
            },
        },
    },
    {
        "name": "get_team_record",
        "description": (
            "Get a team's full tournament record: wins, draws, losses, goals for/"
            "against, and furthest stage reached. Use for questions like 'how did "
            "Mexico perform' or 'what was Argentina's record'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "team_name": {"type": "string", "description": "Team name, e.g. 'Mexico'."},
            },
            "required": ["team_name"],
        },
    },
    {
        "name": "get_match_result",
        "description": (
            "Get the exact result of a specific match between two named teams, "
            "including score, stage, date, venue and player of the match."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "team_a": {"type": "string", "description": "First team's name."},
                "team_b": {"type": "string", "description": "Second team's name."},
            },
            "required": ["team_a", "team_b"],
        },
    },
    {
        "name": "get_player_stats",
        "description": (
            "Get a specific player's tournament statistics: goals, assists, "
            "matches played, cards, rating."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "player_name": {"type": "string", "description": "Player's name."},
            },
            "required": ["player_name"],
        },
    },
    {
        "name": "get_tournament_champion",
        "description": (
            "Get the 2026 World Cup champion and runner-up, from the Final match "
            "result. Use for questions like 'who won the World Cup'."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "search_knowledge_base",
        "description": (
            "Search a knowledge base of natural-language summaries about World Cup "
            "2026 teams, players, and matches. Use for descriptive or narrative "
            "questions that aren't a single precise stat, e.g. 'tell me about "
            "Mexico's tournament' or 'what happened in the France vs Spain game'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."},
                "top_k": {
                    "type": "integer",
                    "description": "How many results to retrieve (default 5).",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_web",
        "description": (
            "Search the live web for information not covered by the World Cup "
            "database or knowledge base - e.g. general World Cup rules, context "
            "not captured in the dataset, or anything outside the tournament's "
            "own data."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."},
            },
            "required": ["query"],
        },
    },
]
