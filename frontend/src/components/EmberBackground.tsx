import { useEffect, useRef } from "react";

// Slow-drifting embers, echoing the particles in the trophy artwork.
// Kept sparse on purpose: it's atmosphere, not a show.
const COLORS = ["226,182,74", "224,54,75", "58,111,242"];

type Ember = { x: number; y: number; r: number; vy: number; vx: number; a: number; c: string };

export default function EmberBackground() {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current!;
    const ctx = canvas.getContext("2d")!;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let raf = 0;
    let embers: Ember[] = [];

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const count = Math.round((window.innerWidth * window.innerHeight) / 32000);
      embers = Array.from({ length: count }, () => spawn(true));
    };

    const spawn = (anywhere: boolean): Ember => ({
      x: Math.random() * window.innerWidth,
      y: anywhere ? Math.random() * window.innerHeight : window.innerHeight + 10,
      r: Math.random() * 1.6 + 0.4,
      vy: -(Math.random() * 0.25 + 0.08),
      vx: (Math.random() - 0.5) * 0.12,
      a: Math.random() * 0.5 + 0.2,
      c: COLORS[Math.random() < 0.6 ? 0 : Math.random() < 0.5 ? 1 : 2],
    });

    const draw = () => {
      ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
      for (const e of embers) {
        ctx.beginPath();
        ctx.fillStyle = `rgba(${e.c},${e.a})`;
        ctx.shadowColor = `rgba(${e.c},0.8)`;
        ctx.shadowBlur = 6;
        ctx.arc(e.x, e.y, e.r, 0, Math.PI * 2);
        ctx.fill();
      }
    };

    const tick = () => {
      embers = embers.map((e) => {
        const n = { ...e, x: e.x + e.vx, y: e.y + e.vy };
        return n.y < -10 ? spawn(false) : n;
      });
      draw();
      raf = requestAnimationFrame(tick);
    };

    resize();
    window.addEventListener("resize", resize);
    if (reduced) draw();
    else raf = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={ref}
      aria-hidden
      style={{ position: "fixed", inset: 0, width: "100%", height: "100%", pointerEvents: "none", zIndex: 0 }}
    />
  );
}
