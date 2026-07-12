/**
 * Server-side proxy to the backend's GET /health — the header's live
 * status pill polls this, never the backend directly, keeping API_URL
 * server-side only (same invariant as app/api/analyze/route.ts).
 */
import { NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

export async function GET() {
  try {
    const res = await fetch(`${API_URL}/health`, { cache: "no-store" });
    if (!res.ok) return NextResponse.json({ status: "offline" }, { status: 200 });
    return NextResponse.json({ status: "online" });
  } catch {
    return NextResponse.json({ status: "offline" });
  }
}
