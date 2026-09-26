import { useState } from "react";
import { Box, Button, Chip, Collapse, Stack, Typography } from "@mui/material";
import { describeTool, type ToolCall } from "../api/agent";
import { tokens } from "../theme/theme";

const toneColor = { gold: tokens.gold, blue: tokens.floodBlue, red: tokens.floodRed };

// Shows which data sources the agent chose, so the routing is visible.
export default function AnswerSources({ calls }: { calls: ToolCall[] }) {
  const [open, setOpen] = useState(false);
  if (calls.length === 0) return null;

  return (
    <Box sx={{ mt: 2 }}>
      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" alignItems="center">
        <Typography variant="body2" color="text.secondary" sx={{ mr: 0.5 }}>
          How I answered:
        </Typography>
        {calls.map((c, i) => {
          const { label, tone } = describeTool(c.name);
          return (
            <Chip
              key={i}
              size="small"
              label={label}
              variant="outlined"
              sx={{ borderColor: toneColor[tone], color: toneColor[tone] }}
            />
          );
        })}
        <Button size="small" onClick={() => setOpen((o) => !o)} aria-expanded={open} sx={{ ml: "auto" }}>
          {open ? "Hide details" : "Show details"}
        </Button>
      </Stack>

      <Collapse in={open}>
        <Stack spacing={1.5} sx={{ mt: 1.5 }}>
          {calls.map((c, i) => (
            <Box key={i} sx={{ bgcolor: tokens.night, borderRadius: 2, p: 1.5, border: 1, borderColor: "divider" }}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                {c.name}
              </Typography>
              <Box
                component="pre"
                sx={{ m: 0, fontSize: 12.5, color: "text.secondary", overflowX: "auto", maxHeight: 220, whiteSpace: "pre-wrap" }}
              >
                {JSON.stringify({ input: c.input, result: c.result }, null, 2)}
              </Box>
            </Box>
          ))}
        </Stack>
      </Collapse>
    </Box>
  );
}
