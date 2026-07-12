/**
 * Serves the branded API reference at this app's root — a separate
 * "virtual directory" from the playground, its own app/port. The spec
 * is fetched server-side from API_URL at REQUEST time (not baked in at
 * build time) and inlined via Scalar's `content` field, so the browser
 * never needs direct network access to the backend — only this app's
 * own origin, which matters inside the compose network where the
 * backend's address (e.g. http://api:8000) isn't browser-reachable.
 */
import { ApiReference } from "@scalar/nextjs-api-reference";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

// Slack-purple accent on top of Scalar's closest built-in preset —
// same brand this whole demo suite (playground, mcp-chat-client) uses.
const BRAND_CSS = `
  :root {
    --scalar-color-accent: #4a154b;
  }
  .light-mode {
    --scalar-color-accent: #4a154b;
  }
  .dark-mode {
    --scalar-color-accent: #a067a6;
  }
  .scalar-app .t-doc__sidebar .sidebar-heading,
  .scalar-app .sidebar-search {
    --scalar-sidebar-color-active: #4a154b;
  }
`;

export async function GET() {
  let spec: unknown;
  try {
    const res = await fetch(`${API_URL}/openapi.json`, { cache: "no-store" });
    if (!res.ok) throw new Error(`backend returned ${res.status}`);
    spec = await res.json();
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return new Response(
      `<!doctype html><html><body style="font-family:system-ui;padding:3rem;color:#4a154b">` +
        `<h1>Couldn't load the API reference</h1>` +
        `<p>Fetching <code>${API_URL}/openapi.json</code> failed: ${message}</p>` +
        `<p>Confirm the backend is running and API_URL is set correctly.</p>` +
        `</body></html>`,
      { status: 502, headers: { "Content-Type": "text/html" } }
    );
  }

  const handler = ApiReference({
    content: spec as Record<string, unknown>,
    theme: "purple",
    pageTitle: "agent-job-matcher — API Reference",
    customCss: BRAND_CSS,
    _integration: "nextjs",
  });

  return handler();
}
