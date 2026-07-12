"use client";

import { useEffect, useState } from "react";
import { Menu, Briefcase } from "lucide-react";
import { SidebarForm } from "@/components/playground/sidebar-form";
import { ResultsPanel } from "@/components/playground/results-panel";
import { StatusPill } from "@/components/playground/status-pill";
import { NavRail } from "@/components/playground/nav-rail";
import { useBackendStatus } from "@/lib/use-backend-status";
import { JobOutcome } from "@/lib/types";

export default function Home() {
  const [results, setResults] = useState<JobOutcome[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const status = useBackendStatus();

  // Same collapse-persistence pattern as privacyshield's App.tsx.
  const [collapsed, setCollapsed] = useState(false);
  useEffect(() => {
    setCollapsed(localStorage.getItem("playground:nav-collapsed") === "1");
  }, []);
  useEffect(() => {
    localStorage.setItem("playground:nav-collapsed", collapsed ? "1" : "0");
  }, [collapsed]);

  return (
    <div className="flex h-screen">
      <NavRail collapsed={collapsed} />

      <div className="flex min-h-0 min-w-0 flex-1 flex-col">
        <header className="flex h-16 shrink-0 items-center gap-4 border-b bg-card px-4 sm:px-6">
          <button
            type="button"
            onClick={() => setCollapsed((c) => !c)}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            className="hidden h-9 w-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground lg:inline-flex"
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="flex min-w-0 items-center gap-3">
            <Briefcase className="h-5 w-5 shrink-0 text-brand-700" />
            <div className="min-w-0">
              <h1 className="truncate text-base font-semibold">Analyze fit</h1>
              <p className="truncate text-xs text-muted-foreground">
                Resume + job links → evidence-grounded fit reports
              </p>
            </div>
          </div>

          <div className="ml-auto shrink-0">
            <StatusPill status={status} />
          </div>
        </header>

        <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
          <aside className="w-full shrink-0 border-b lg:w-96 lg:border-b-0 lg:border-r">
            <SidebarForm
              loading={loading}
              onSubmitStart={() => {
                setLoading(true);
                setError(null);
              }}
              onSubmitSuccess={(data) => {
                setResults(data);
                setLoading(false);
              }}
              onSubmitError={(message) => {
                setError(message);
                setLoading(false);
              }}
              onClear={() => {
                setResults(null);
                setError(null);
              }}
            />
          </aside>

          <main className="min-h-0 min-w-0 flex-1 overflow-y-auto bg-muted/20 px-5 py-6 lg:px-8">
            <ResultsPanel results={results} loading={loading} error={error} />
          </main>
        </div>
      </div>
    </div>
  );
}
