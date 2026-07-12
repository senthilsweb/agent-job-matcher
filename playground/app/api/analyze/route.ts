/**
 * Server-side proxy to the backend's POST /analyze. Keeps the backend's
 * address (a compose-network hostname in the containerized stack, e.g.
 * http://api:8000) out of client-side code entirely — the browser only
 * ever talks to this same-origin route.
 *
 * No re-scoring or re-shaping of the response: the backend's typed
 * JobOutcome array is passed through byte-for-byte.
 */
import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest) {
  const incoming = await request.formData();

  const resume = incoming.get("resume");
  const jobs = incoming.getAll("jobs");

  if (!(resume instanceof File) || jobs.length === 0) {
    return NextResponse.json(
      { error: "provide a resume file and at least one job link" },
      { status: 422 }
    );
  }

  const outgoing = new FormData();
  outgoing.append("resume", resume, resume.name);
  for (const job of jobs) {
    outgoing.append("jobs", job as string);
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      body: outgoing,
    });
  } catch {
    return NextResponse.json(
      { error: `backend unreachable at ${API_URL}` },
      { status: 502 }
    );
  }

  const body = await upstream.text();
  return new NextResponse(body, {
    status: upstream.status,
    headers: { "Content-Type": "application/json" },
  });
}
