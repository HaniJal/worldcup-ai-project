import { Box, Typography } from "@mui/material";
import { tokens } from "../theme/theme";

// Compact header: title on the left, the trophy artwork small on the right,
// so the question box sits near the top of the screen.
export default function Hero() {
  return (
    <Box
      component="header"
      sx={{
        maxWidth: 1100,
        mx: "auto",
        px: { xs: 2, sm: 4, md: 8 },
        pt: { xs: 2, md: 3 },
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 2,
      }}
    >
      <Typography
        variant="h1"
        component="h1"
        sx={{ fontSize: "clamp(2.25rem, 6vw, 4.5rem)", whiteSpace: "nowrap" }}
      >
        World Cup 2026
      </Typography>

      <Box
        sx={{
          position: "relative",
          flexShrink: 0,
          width: { xs: 110, sm: 170, md: 220 },
          // floodlight glow behind the picture, as in the artwork
          "&::before": {
            content: '""',
            position: "absolute",
            inset: "5%",
            background: `radial-gradient(circle at 30% 50%, ${tokens.floodRed}44, transparent 60%),
                         radial-gradient(circle at 75% 45%, ${tokens.floodBlue}44, transparent 60%)`,
            filter: "blur(24px)",
          },
        }}
      >
        <Box
          component="img"
          src="/hero.jpg"
          alt="The World Cup trophy beside the 2026 match ball"
          sx={{
            position: "relative",
            display: "block",
            width: "100%",
            height: "auto",
            // soften the edges so the picture melts into the page
            maskImage: "radial-gradient(ellipse at center, black 50%, transparent 74%)",
          }}
        />
      </Box>
    </Box>
  );
}
