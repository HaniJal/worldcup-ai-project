import { tokens } from "../theme/theme";

export default function Ball({ size = 44 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="-10 -10 20 20" aria-hidden>
      <circle r="9.4" fill={tokens.chalk} />
      <path d="M-8 -3 Q 0 -9 7 -5" stroke={tokens.floodRed} strokeWidth="2" fill="none" strokeLinecap="round" />
      <path d="M-7 4 Q 0 0 8 3" stroke={tokens.floodBlue} strokeWidth="2" fill="none" strokeLinecap="round" />
      <path d="M-2 8 Q 2 2 1 -8" stroke={tokens.gold} strokeWidth="1.6" fill="none" strokeLinecap="round" />
    </svg>
  );
}
