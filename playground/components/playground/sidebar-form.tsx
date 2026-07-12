"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { ResumeDropzone } from "@/components/playground/resume-dropzone";
import { JobLinkList } from "@/components/playground/job-link-list";
import { JobOutcome } from "@/lib/types";
import { Briefcase, Loader2, RotateCcw, Sparkles } from "lucide-react";

interface SidebarFormProps {
  onSubmitStart: () => void;
  onSubmitSuccess: (results: JobOutcome[]) => void;
  onSubmitError: (message: string) => void;
  onClear: () => void;
  loading: boolean;
}

export function SidebarForm({
  onSubmitStart,
  onSubmitSuccess,
  onSubmitError,
  onClear,
  loading,
}: SidebarFormProps) {
  const [resume, setResume] = useState<File | null>(null);
  const [links, setLinks] = useState<string[]>([""]);

  const validLinks = links.map((l) => l.trim()).filter(Boolean);
  const canSubmit = resume !== null && validLinks.length > 0 && !loading;
  const hasContent = resume !== null || links.some((l) => l.trim());

  const handleClear = () => {
    setResume(null);
    setLinks([""]);
    onClear();
  };

  const handleSubmit = async () => {
    if (!resume || validLinks.length === 0) return;
    onSubmitStart();

    const body = new FormData();
    body.append("resume", resume, resume.name);
    for (const link of validLinks) body.append("jobs", link);

    try {
      const res = await fetch("/api/analyze", { method: "POST", body });
      const data = await res.json();
      if (!res.ok) {
        onSubmitError(data?.error ?? `Request failed (${res.status})`);
        return;
      }
      onSubmitSuccess(data as JobOutcome[]);
    } catch {
      onSubmitError("Could not reach the playground's proxy route.");
    }
  };

  return (
    // Two regions, not one scrolling column: the form content scrolls
    // independently while the Submit footer stays pinned via `sticky
    // bottom-0` — with enough job-link rows the form alone can exceed the
    // viewport, and the primary action must never require a scroll to reach
    // (matches the always-visible action bar every other UI in this demo
    // suite uses, e.g. mcp-chat-client's ChatInput).
    <Card className="flex h-full flex-col rounded-none border-0 border-r ring-0 shadow-none py-0">
      <CardHeader className="shrink-0 border-b py-4">
        <CardTitle className="flex items-center gap-2 text-brand-700">
          <Briefcase className="size-4" />
          Analyze fit
        </CardTitle>
        <CardDescription>
          Upload a resume and one or more job links to get a scored report.
        </CardDescription>
      </CardHeader>

      <CardContent className="min-h-0 flex-1 space-y-5 overflow-y-auto py-5">
        <div className="space-y-1.5">
          <Label>1. Resume</Label>
          <ResumeDropzone file={resume} onChange={setResume} />
        </div>

        <div className="space-y-1.5">
          <Label>2. Job links</Label>
          <JobLinkList links={links} onChange={setLinks} />
        </div>
      </CardContent>

      <div className="flex shrink-0 items-center gap-2 border-t bg-card p-4">
        <Button
          variant="ghost"
          disabled={!hasContent || loading}
          onClick={handleClear}
        >
          <RotateCcw className="size-4" />
          Clear
        </Button>
        <Button
          className="flex-1 bg-brand-700 text-white hover:bg-brand-800"
          disabled={!canSubmit}
          onClick={handleSubmit}
        >
          {loading ? (
            <>
              <Loader2 className="size-4 animate-spin" />
              Analyzing…
            </>
          ) : (
            <>
              <Sparkles className="size-4" />
              Analyze fit
            </>
          )}
        </Button>
      </div>
    </Card>
  );
}
