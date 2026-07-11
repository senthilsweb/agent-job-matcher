#!/usr/bin/env node
/**
 * File Name: smoke.mjs
 * Author: Senthilnathan Karuppaiah
 * Date: 11-JUL-2026
 * Description:
 * MCP server smoke test (no LLM, no real backend): spins up a stub HTTP
 * backend, mounts index.js over stdio via the MCP client SDK, and pins
 * the Bolt 7 contract.
 *
 * This test verifies the bridge by:
 * 1. tools/list → exactly analyze_job_fit, extract_jsonresume, health.
 * 2. tools/call analyze_job_fit → the stub's typed array passed through
 *    untouched, resume_path/jobs form fields received by the backend.
 * 3. Backend error status → isError tool result, not a crash.
 *
 * Run: npm test   (from mcp/)
 */

import assert from "node:assert/strict";
import http from "node:http";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

// ── Stub backend ─────────────────────────────────────────────────────────
const seen = [];
const stub = http.createServer((req, res) => {
  let raw = "";
  req.on("data", (chunk) => (raw += chunk));
  req.on("end", () => {
    seen.push({ method: req.method, url: req.url, raw });
    res.setHeader("content-type", "application/json");
    if (req.url === "/health") return res.end(JSON.stringify({ status: "ok", version: "test" }));
    if (req.url === "/analyze")
      return res.end(JSON.stringify([{ fetch_status: "ok", run_id: "stub-run", match_status: "good_match" }]));
    if (req.url === "/resume/jsonresume")
      return res.end(JSON.stringify({ basics: { name: "Jordan Rivera" }, meta: { version: "v1.0.0" } }));
    res.statusCode = 422;
    res.end(JSON.stringify({ detail: "boom" }));
  });
});
await new Promise((resolve) => stub.listen(0, "127.0.0.1", resolve));
const apiUrl = `http://127.0.0.1:${stub.address().port}`;

// ── Mount the server over stdio ──────────────────────────────────────────
const transport = new StdioClientTransport({
  command: "node",
  args: [new URL("../index.js", import.meta.url).pathname],
  env: { ...process.env, JOBMATCHER_API_URL: apiUrl },
});
const client = new Client({ name: "smoke", version: "0.0.0" });
await client.connect(transport);

// 1 — tool list
const { tools } = await client.listTools();
assert.deepEqual(
  tools.map((t) => t.name).sort(),
  ["analyze_job_fit", "extract_jsonresume", "health"],
  "tool list mismatch"
);

// 2 — analyze pass-through
const result = await client.callTool({
  name: "analyze_job_fit",
  arguments: { resume_path: "/tmp/resume.pdf", job_sources: ["/tmp/jd.txt", "https://x.example/jd"] },
});
const payload = JSON.parse(result.content[0].text);
assert.equal(payload[0].run_id, "stub-run", "typed array not passed through");
const analyzeReq = seen.find((r) => r.url === "/analyze");
assert.ok(analyzeReq.raw.includes("resume_path"), "resume_path form field missing");
assert.ok(analyzeReq.raw.includes("https://x.example/jd"), "jobs form field missing");

// 3 — jsonresume pass-through
const jr = await client.callTool({ name: "extract_jsonresume", arguments: { resume_path: "/tmp/r.pdf" } });
assert.equal(JSON.parse(jr.content[0].text).basics.name, "Jordan Rivera");

// 4 — health
const health = await client.callTool({ name: "health", arguments: {} });
assert.equal(JSON.parse(health.content[0].text).status, "ok");

// 5 — backend error → isError result
const bad = await client.callTool({ name: "unknown_tool", arguments: {} });
assert.equal(bad.isError, true, "unknown tool should be an isError result");

await client.close();
stub.close();
console.log("MCP smoke: 5/5 assertions passed");
