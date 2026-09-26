import { createTheme } from "@mui/material/styles";

// Palette pulled from the reference image: night-match navy,
// trophy gold, and the red/blue floodlight glow.
export const tokens = {
  night: "#0A0E1A",
  surface: "#131A2E",
  surfaceRaised: "#1A2340",
  gold: "#E2B64A",
  goldDeep: "#A8822A",
  floodRed: "#E0364B",
  floodBlue: "#3A6FF2",
  chalk: "#EEF1F7",
  mist: "#9AA3B8",
};

export const theme = createTheme({
  palette: {
    mode: "dark",
    background: { default: tokens.night, paper: tokens.surface },
    primary: { main: tokens.gold, contrastText: tokens.night },
    secondary: { main: tokens.floodBlue },
    error: { main: tokens.floodRed },
    text: { primary: tokens.chalk, secondary: tokens.mist },
    divider: "rgba(154,163,184,0.16)",
  },
  shape: { borderRadius: 14 },
  typography: {
    fontFamily: '"Barlow", "Segoe UI", system-ui, sans-serif',
    h1: {
      fontFamily: '"Big Shoulders Display", "Impact", sans-serif',
      fontWeight: 800,
      fontSize: "clamp(2.75rem, 7vw, 5.25rem)",
      lineHeight: 0.95,
      letterSpacing: "-0.01em",
    },
    h2: {
      fontFamily: '"Big Shoulders Display", "Impact", sans-serif',
      fontWeight: 600,
      fontSize: "1.75rem",
      lineHeight: 1.1,
    },
    body1: { fontSize: "1.0625rem", lineHeight: 1.6 },
    body2: { fontSize: "0.9375rem", lineHeight: 1.5 },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: { backgroundColor: tokens.night },
        "*:focus-visible": { outline: `2px solid ${tokens.gold}`, outlineOffset: 2 },
        "@media (prefers-reduced-motion: reduce)": {
          "*": { animation: "none !important", transition: "none !important" },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { textTransform: "none", fontWeight: 600, borderRadius: 999, paddingInline: 22 },
      },
    },
    MuiChip: { styleOverrides: { root: { fontWeight: 500 } } },
  },
});
