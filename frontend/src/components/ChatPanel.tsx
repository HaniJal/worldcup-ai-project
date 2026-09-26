import { useEffect, useRef, useState, type FormEvent } from "react";
import { Alert, Box, Button, Chip, InputBase, Paper, Stack, Typography } from "@mui/material";
import { askAgent, AskError, type ToolCall } from "../api/agent";
import type { ShotState } from "./shot";
import AnswerSources from "./AnswerSources";
import { tokens } from "../theme/theme";

type Message =
  | { role: "user"; text: string }
  | { role: "assistant"; text: string; calls: ToolCall[] }
  | { role: "error"; text: string };

const SUGGESTIONS = [
  "Who won the 2026 final?",
  "Who finished as top scorer?",
  "How far did Morocco get?",
  "Which team conceded the fewest goals?",
];

const STATUS: Record<ShotState, string> = {
  idle: "Ask a question and take a shot at goal.",
  thinking: "Working out which data to check…",
  scored: "Answered.",
  missed: "That one didn't go in.",
};

export default function ChatPanel({
  shot,
  onShot,
}: {
  shot: ShotState;
  onShot: (s: ShotState) => void;
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [messages, shot]);

  const ask = async (question: string) => {
    const q = question.trim();
    if (!q || shot === "thinking") return;
    setDraft("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    onShot("thinking");
    try {
      const res = await askAgent(q);
      setMessages((m) => [...m, { role: "assistant", text: res.answer, calls: res.tool_calls }]);
      onShot("scored");
    } catch (err) {
      const text = err instanceof AskError ? err.message : "Something went wrong. Try again.";
      setMessages((m) => [...m, { role: "error", text }]);
      onShot("missed");
    }
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    void ask(draft);
  };

  return (
    <Paper
      elevation={0}
      sx={{
        position: "relative",
        border: 1,
        borderColor: "divider",
        borderRadius: 5,
        overflow: "hidden",
        background: `linear-gradient(160deg, ${tokens.surfaceRaised}ee 0%, ${tokens.surface}f2 55%)`,
        backdropFilter: "blur(6px)",
      }}
    >
      <Typography
        variant="body2"
        color="text.secondary"
        aria-live="polite"
        sx={{ px: { xs: 2.5, sm: 4 }, py: 1.5, borderBottom: 1, borderColor: "divider" }}
      >
        {STATUS[shot]}
      </Typography>

      {/* conversation */}
      <Box sx={{ px: { xs: 2.5, sm: 4 }, py: 3, minHeight: 220 }}>
        {messages.length === 0 ? (
          <Box>
            <Typography color="text.secondary" sx={{ mb: 2, maxWidth: "60ch" }}>
              Ask about results, scorers, or how a team's tournament went. The answer shows which
              sources were checked to get it.
            </Typography>
            <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
              {SUGGESTIONS.map((s) => (
                <Chip key={s} label={s} onClick={() => ask(s)} variant="outlined" clickable />
              ))}
            </Stack>
          </Box>
        ) : (
          <Stack spacing={2.5}>
            {messages.map((m, i) =>
              m.role === "user" ? (
                <Box
                  key={i}
                  sx={{
                    alignSelf: "flex-end",
                    maxWidth: "80%",
                    bgcolor: tokens.gold,
                    color: tokens.night,
                    px: 2,
                    py: 1.25,
                    borderRadius: "18px 18px 4px 18px",
                    fontWeight: 500,
                  }}
                >
                  {m.text}
                </Box>
              ) : m.role === "assistant" ? (
                <Box key={i} sx={{ maxWidth: "68ch", borderLeft: 3, borderColor: tokens.gold, pl: 2 }}>
                  <Typography sx={{ whiteSpace: "pre-wrap" }}>{m.text}</Typography>
                  <AnswerSources calls={m.calls} />
                </Box>
              ) : (
                <Alert key={i} severity="error" variant="outlined" sx={{ maxWidth: "68ch" }}>
                  {m.text}
                </Alert>
              )
            )}
            <div ref={endRef} />
          </Stack>
        )}
      </Box>

      {/* input */}
      <Box
        component="form"
        onSubmit={onSubmit}
        sx={{
          display: "flex",
          gap: 1,
          alignItems: "center",
          m: { xs: 1.5, sm: 2.5 },
          mt: 0,
          p: 0.75,
          pl: 2.5,
          borderRadius: 999,
          bgcolor: tokens.night,
          border: 1,
          borderColor: "divider",
          "&:focus-within": { borderColor: tokens.gold },
        }}
      >
        <InputBase
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Who scored in the final?"
          inputProps={{ "aria-label": "Your question", maxLength: 500 }}
          sx={{ flex: 1, fontSize: "1rem" }}
        />
        <Button type="submit" variant="contained" disabled={!draft.trim() || shot === "thinking"}>
          Ask
        </Button>
      </Box>
    </Paper>
  );
}
