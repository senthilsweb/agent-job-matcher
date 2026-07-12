"use client";

import { Accordion } from "@/components/ui/accordion";
import { ReportCard } from "@/components/playground/report-card";
import { JobOutcome } from "@/lib/types";
import { FileSearch2 } from "lucide-react";

interface ResultsPanelProps {
  results: JobOutcome[] | null;
  loading: boolean;
  error: string | null;
}

export function ResultsPanel({ results, loading, error }: ResultsPanelProps) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="h-24 animate-pulse rounded-xl border bg-muted/40"
          />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">
        {error}
      </div>
    );
  }

  if (!results) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 rounded-xl border border-dashed py-16 text-center text-muted-foreground">
        <FileSearch2 className="size-8 text-brand-400" />
        <p className="max-w-xs text-sm">
          Upload a resume and add one or more job links, then submit — each
          job's evidence-grounded fit report shows up here as a compact card.
        </p>
      </div>
    );
  }

  return (
    // Base UI's Accordion (not Radix — this repo's shadcn init uses the
    // "Base" library) single-expands by default: `multiple` defaults to
    // false, unlike Radix's type="single" collapsible spelling.
    <Accordion className="space-y-3">
      {results.map((outcome, i) => (
        <ReportCard key={outcome.job_source + i} outcome={outcome} value={String(i)} />
      ))}
    </Accordion>
  );
}
