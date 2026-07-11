#!/usr/bin/env node
/**
 * File Name: index.js
 * Author: Senthilnathan Karuppaiah
 * Date: 11-JUL-2026
 * Description:
 * MCP server for agent-job-matcher — modelled on ctms-mcp-server's MCP
 * portion only (openspec/changes/add-job-matcher-cli, Bolt 7; ADR 0001).
 *
 * This server bridges MCP to the backend by:
 * 1. Declaring exactly three tools — analyze_job_fit, extract_jsonresume,
 *    health — whose input schemas mirror the backend REST contracts.
 * 2. Passing every tools/call straight through to the backend REST API at
 *    JOBMATCHER_API_URL via fetch(); results are the backend's typed JSON,
 *    returned untouched. No business logic, no state, NO REST endpoints of
 *    its own (the agent service in ./agent-service is the HTTP face).
 * 3. Speaking stdio only — mounted by Claude Desktop (configs/) and by the
 *    agent service's pydantic-ai MCP client.
 *
 * Environment Variables:
 * - JOBMATCHER_API_URL: backend base URL (default: http://localhost:8000)
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const API_URL = (process.env.JOBMATCHER_API_URL || "http://localhost:8000").replace(/\/$/, "");

const server = new Server(
  { name: "jobmatcher-mcp", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// ── Tool declarations — input schemas mirror the REST contracts ─────────
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "analyze_job_fit",
      description:
        "Analyze a resume against one or more job sources. Returns a typed JSON array of " +
        "per-job outcomes (JobReport | JobFetchFailure): evidence-grounded skill matches and a " +
        "deterministic 100-point score with match band. The LLM never produces the score.",
      inputSchema: {
        type: "object",
        properties: {
          resume_path: {
            type: "string",
            description: "Server-side path to the resume file (PDF, DOCX, TXT, MD)",
          },
          job_sources: {
            type: "array",
            items: { type: "string" },
            description: "Job sources: public http/https URLs and/or server-side JD file paths",
          },
        },
        required: ["resume_path", "job_sources"],
      },
    },
    {
      name: "extract_jsonresume",
      description:
        "Convert a resume file into a strongly-typed JSON Resume v1.0.0 document " +
        "(jsonresume.org). Contact details are grounding-guarded — never invented.",
      inputSchema: {
        type: "object",
        properties: {
          resume_path: {
            type: "string",
            description: "Server-side path to the resume file (PDF, DOCX, TXT, MD)",
          },
        },
        required: ["resume_path"],
      },
    },
    {
      name: "health",
      description: "Backend liveness and version.",
      inputSchema: { type: "object", properties: {}, required: [] },
    },
  ],
}));

// ── Pass-through call handler ────────────────────────────────────────────
async function callBackend(name, args) {
  if (name === "health") {
    const response = await fetch(`${API_URL}/health`);
    return { status: response.status, body: await response.json() };
  }
  const form = new FormData();
  form.append("resume_path", args.resume_path);
  if (name === "analyze_job_fit") {
    for (const source of args.job_sources || []) form.append("jobs", source);
    const response = await fetch(`${API_URL}/analyze`, { method: "POST", body: form });
    return { status: response.status, body: await response.json() };
  }
  if (name === "extract_jsonresume") {
    const response = await fetch(`${API_URL}/resume/jsonresume`, { method: "POST", body: form });
    return { status: response.status, body: await response.json() };
  }
  throw new Error(`unknown tool: ${name}`);
}

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  try {
    const { status, body } = await callBackend(name, args || {});
    if (status >= 400) {
      return {
        isError: true,
        content: [{ type: "text", text: `backend error (HTTP ${status}): ${JSON.stringify(body)}` }],
      };
    }
    return { content: [{ type: "text", text: JSON.stringify(body, null, 2) }] };
  } catch (error) {
    return {
      isError: true,
      content: [{ type: "text", text: `tool failed: ${error.message}` }],
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
console.error(`jobmatcher-mcp ready (backend: ${API_URL})`);
