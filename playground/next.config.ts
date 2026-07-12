import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  // Pins the workspace root to this app — without it, Turbopack finds an
  // unrelated bun.lock higher up in the home directory and infers the
  // wrong root (harmless, but noisy on every build).
  turbopack: {
    root: path.join(__dirname),
  },
  // Standalone output: the Dockerfile copies just .next/standalone +
  // .next/static instead of the whole node_modules tree.
  output: "standalone",
};

export default nextConfig;
