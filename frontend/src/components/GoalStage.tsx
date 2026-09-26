import { forwardRef, type ReactNode } from "react";
import { Box } from "@mui/material";
import { keyframes } from "@mui/material/styles";
import { tokens } from "../theme/theme";
import type { ShotState } from "./shot";

// A full-width goal that frames the chat: posts at the page edges,
// crossbar above the panel, and a diamond-mesh net behind everything.
const bulge = keyframes`
  0%, 45% { transform: scale(1) translateY(0); }
  60% { transform: scale(1.025, 1.04) translateY(-6px); }
  78% { transform: scale(0.995) translateY(1px); }
  100% { transform: scale(1) translateY(0); }
`;
const ripple = keyframes`
  0%, 45% { opacity: 0; transform: scale(0.2); }
  60% { opacity: 0.9; }
  100% { opacity: 0; transform: scale(2.4); }
`;
const rattle = keyframes`
  0%, 30%, 100% { transform: translateX(0); }
  40% { transform: translateX(-4px); }
  52% { transform: translateX(3px); }
  64% { transform: translateX(-2px); }
  76% { transform: translateX(1px); }
`;

// Where the ball lands, as a fraction of the stage's width / px from its top.
export const IMPACT = { x: 0.72, y: 36 };

type Props = { state: ShotState; shotId: number; children: ReactNode };

const GoalStage = forwardRef<HTMLDivElement, Props>(function GoalStage({ state, shotId, children }, ref) {
  const post = { xs: 5, md: 8 };
  return (
    <Box ref={ref} component="section" sx={{ position: "relative", mt: { xs: 1, md: 1.5 } }}>
      {/* net */}
      <Box
        key={`net-${shotId}`}
        aria-hidden
        sx={{
          position: "absolute",
          inset: 0,
          transformOrigin: "50% 0",
          animation: state === "scored" ? `${bulge} 1.3s ease-out` : "none",
          backgroundImage: `
            repeating-linear-gradient(45deg, rgba(238,241,247,0.09) 0 1px, transparent 1px 22px),
            repeating-linear-gradient(-45deg, rgba(238,241,247,0.09) 0 1px, transparent 1px 22px),
            radial-gradient(ellipse at 50% 0%, ${tokens.surfaceRaised} 0%, ${tokens.night} 75%)`,
          maskImage: "linear-gradient(180deg, black 60%, transparent 100%)",
        }}
      >
        {/* flash where the ball hits */}
        <Box
          sx={{
            position: "absolute",
            left: `${IMPACT.x * 100}%`,
            top: IMPACT.y,
            width: 220,
            height: 220,
            ml: "-110px",
            mt: "-110px",
            borderRadius: "50%",
            background: `radial-gradient(circle, ${tokens.gold}66 0%, transparent 65%)`,
            opacity: 0,
            animation: state === "scored" ? `${ripple} 1.3s ease-out` : "none",
          }}
        />
      </Box>

      {/* frame */}
      <Box
        key={`frame-${shotId}`}
        aria-hidden
        sx={{
          position: "absolute",
          inset: 0,
          borderTop: post,
          borderLeft: post,
          borderRight: post,
          borderColor: tokens.chalk,
          borderTopLeftRadius: 6,
          borderTopRightRadius: 6,
          boxShadow: `0 -10px 50px -20px ${tokens.floodBlue}`,
          animation: state === "missed" ? `${rattle} 0.9s ease-out` : "none",
          pointerEvents: "none",
        }}
      />

      {/* goal line */}
      <Box aria-hidden sx={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 2, bgcolor: tokens.chalk, opacity: 0.4 }} />

      <Box
        sx={{
          position: "relative",
          px: { xs: 2, sm: 4, md: 8 },
          pt: { xs: 6, md: 8 },
          pb: { xs: 3, md: 6 },
          maxWidth: 1100,
          mx: "auto",
        }}
      >
        {children}
      </Box>
    </Box>
  );
});

export default GoalStage;
