import { useEffect, useRef, type RefObject } from "react";
import { Box } from "@mui/material";
import Ball from "./Ball";
import { IMPACT } from "./GoalStage";
import type { ShotState } from "./shot";

const SIZE = 44;

// The ball lives above the whole page. It's kept up in the corner while
// the agent thinks, then crosses the screen into the net (or off the post).
export default function BallLayer({
  state,
  shotId,
  stageRef,
}: {
  state: ShotState;
  shotId: number;
  stageRef: RefObject<HTMLDivElement>;
}) {
  const ballRef = useRef<HTMLDivElement>(null);
  const reduced = typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  useEffect(() => {
    const ball = ballRef.current;
    const stage = stageRef.current;
    if (!ball || !stage || reduced) return;

    const start = { x: 24, y: window.innerHeight - SIZE - 24 };
    const at = (x: number, y: number, rot: number, scale = 1, opacity = 1) => ({
      transform: `translate(${x}px, ${y}px) rotate(${rot}deg) scale(${scale})`,
      opacity,
    });

    let anim: Animation | null = null;

    if (state === "thinking") {
      anim = ball.animate(
        [at(start.x, start.y, 0), at(start.x, start.y - 70, 180), at(start.x, start.y, 360)],
        { duration: 700, iterations: Infinity, easing: "ease-in-out" }
      );
    } else if (state === "scored") {
      const r = stage.getBoundingClientRect();
      const end = { x: r.left + r.width * IMPACT.x - SIZE / 2, y: Math.max(r.top + IMPACT.y, 60) - SIZE / 2 };
      const peak = { x: (start.x + end.x) / 2, y: Math.min(start.y, end.y) - window.innerHeight * 0.25 };
      anim = ball.animate(
        [
          at(start.x, start.y, 0, 1),
          at(peak.x, peak.y, 540, 0.9),
          at(end.x, end.y, 900, 0.7),
          at(end.x + 8, end.y + 14, 960, 0.62, 0),
        ],
        { duration: 1100, easing: "cubic-bezier(.25,.6,.4,1)", fill: "forwards" }
      );
    } else if (state === "missed") {
      const r = stage.getBoundingClientRect();
      const post = { x: r.left + 4, y: r.top + 10 };
      anim = ball.animate(
        [
          at(start.x, start.y, 0),
          at(post.x, post.y, 300),
          at(post.x + 60, post.y + 120, 460, 1, 1),
          at(post.x + 90, window.innerHeight, 600, 1, 0),
        ],
        { duration: 1100, easing: "ease-in", fill: "forwards" }
      );
    } else {
      ball.style.opacity = "0";
    }
    return () => anim?.cancel();
  }, [state, shotId, stageRef, reduced]);

  if (reduced) return null;

  return (
    <Box
      aria-hidden
      sx={{ position: "fixed", inset: 0, pointerEvents: "none", zIndex: 10, overflow: "hidden" }}
    >
      <Box
        ref={ballRef}
        sx={{
          position: "absolute",
          top: 0,
          left: 0,
          width: SIZE,
          height: SIZE,
          opacity: 0,
          filter: "drop-shadow(0 6px 10px rgba(0,0,0,0.5))",
        }}
      >
        <Ball size={SIZE} />
      </Box>
    </Box>
  );
}
