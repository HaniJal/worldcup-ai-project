// Mirrors AgentAskResponse / ToolCallOut in backend/src/features/agent.
export type ToolCall = {
  name: string;
  input: Record<string, unknown>;
  result: unknown;
};

export type AgentAnswer = {
  answer: string;
  tool_calls: ToolCall[];
};

const API_BASE = import.meta.env.VITE_API_URL ?? "";

export class AskError extends Error {}

export async function askAgent(question: string): Promise<AgentAnswer> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/v1/agent/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
  } catch {
    throw new AskError("Can't reach the server. Check that the backend is running.");
  }

  if (res.status === 429) {
    throw new AskError("Too many questions in a short time. Try again in a few minutes.");
  }
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const detail = typeof body?.detail === "string" ? body.detail : null;
    throw new AskError(detail ?? `The server couldn't answer (error ${res.status}).`);
  }
  return res.json();
}

// Turns internal tool names into words a visitor understands.
export function describeTool(name: string): { label: string; tone: "gold" | "blue" | "red" } {
  const n = name.toLowerCase();
  if (n.includes("web")) return { label: "Searched the web", tone: "red" };
  if (n.includes("rag") || n.includes("retriev") || n.includes("document") || n.includes("search"))
    return { label: "Read match reports", tone: "blue" };
  return { label: "Checked tournament stats", tone: "gold" };
}
