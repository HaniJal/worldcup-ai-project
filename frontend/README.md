# World Cup 2026 Analyst: frontend

React + Vite + MUI client for the FastAPI backend.

## Run it

From the project root, with the rest of the stack:

    docker compose up --build

Open http://localhost:5173. Vite forwards `/v1/*` to the `backend` service, so no CORS setup is needed.
Edits in `frontend/src` reload in the browser automatically.

After changing `package.json`, rebuild the image: `docker compose up --build frontend`.

## Production

`npm run build` creates static files in `dist/`. Either serve them from FastAPI, or host them
separately and set `VITE_API_URL` to the backend URL at build time (then enable CORS on FastAPI
for that origin).

## Structure

- `src/api/agent.ts`: calls `POST /v1/agent/ask`, turns 429/503 into readable messages, maps tool names to plain labels
- `src/components/ChatPanel.tsx`: the conversation, suggestions and input
- `src/components/GoalStage.tsx`: the full-width goal (posts, crossbar, net) around the chat, with the net bulge and post rattle
- `src/components/BallLayer.tsx`: the ball that flies across the whole page into the net (or off the post on errors)
- `src/components/AnswerSources.tsx`: which sources the agent used, with raw tool input/output on demand
- `src/components/EmberBackground.tsx`: the drifting particles
- `src/theme/theme.ts`: colors and type
