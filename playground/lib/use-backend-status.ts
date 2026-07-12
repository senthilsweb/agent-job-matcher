"use client";

import { useEffect, useState } from "react";

export type BackendStatus = "checking" | "online" | "offline";

// Mirrors mcp-chat-client's src/demo/DemoApp.tsx useBackendStatus() exactly
// (same poll interval, same three states) — polls this app's own
// /api/health proxy, never the backend directly.
export function useBackendStatus(): BackendStatus {
  const [status, setStatus] = useState<BackendStatus>("checking");

  useEffect(() => {
    let cancelled = false;
    const check = () => {
      fetch("/api/health")
        .then((res) => res.json())
        .then((data) => !cancelled && setStatus(data.status === "online" ? "online" : "offline"))
        .catch(() => !cancelled && setStatus("offline"));
    };
    check();
    const interval = setInterval(check, 5000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return status;
}
