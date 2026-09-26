import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, requests to /v1/* are forwarded to the FastAPI backend, so the
// browser never hits a CORS problem. Inside Docker Compose the backend is
// reachable at http://backend:8000 (set in docker-compose.yml).
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // listen on 0.0.0.0 so the container port is reachable
    port: 5173,
    // file changes from a mounted folder don't always reach the container
    // (Docker Desktop on Windows/Mac), so poll there
    watch: { usePolling: process.env.VITE_USE_POLLING === "true" },
    proxy: {
      "/v1": {
        target: process.env.VITE_BACKEND_URL ?? "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
