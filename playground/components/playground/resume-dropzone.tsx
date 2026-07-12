"use client";

import { useRef, useState } from "react";
import { FileText, Upload, X } from "lucide-react";
import { cn } from "@/lib/utils";

// Mirrors job_matcher.resume.SUPPORTED_EXTENSIONS exactly.
const ACCEPT = ".pdf,.docx,.txt,.md,.markdown";

interface ResumeDropzoneProps {
  file: File | null;
  onChange: (file: File | null) => void;
}

export function ResumeDropzone({ file, onChange }: ResumeDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const handleFiles = (files: FileList | null) => {
    if (files && files.length > 0) onChange(files[0]);
  };

  if (file) {
    return (
      <div className="flex items-center gap-2 rounded-lg border bg-accent/40 px-3 py-2.5">
        <FileText className="size-4 shrink-0 text-brand-700" />
        <span className="min-w-0 flex-1 truncate text-sm font-medium">
          {file.name}
        </span>
        <button
          type="button"
          onClick={() => onChange(null)}
          className="shrink-0 rounded-full p-1 text-muted-foreground hover:bg-muted hover:text-destructive"
          aria-label="Remove resume"
        >
          <X className="size-4" />
        </button>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        handleFiles(e.dataTransfer.files);
      }}
      className={cn(
        "flex w-full flex-col items-center gap-2 rounded-lg border-2 border-dashed px-4 py-8 text-center transition-colors",
        dragging
          ? "border-brand-500 bg-brand-50"
          : "border-border hover:border-brand-400 hover:bg-accent/30"
      )}
    >
      <Upload className="size-6 text-brand-600" />
      <span className="text-sm font-medium">Drop your resume, or click to browse</span>
      <span className="text-xs text-muted-foreground">PDF, DOCX, TXT, or MD</span>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
        // The input is nested inside the button (for a single click target
        // covering the whole dropzone). Without stopping propagation here,
        // the input's own click — triggered programmatically by the
        // button's onClick below — bubbles right back up to that same
        // button handler, re-invoking it and calling .click() a second,
        // reentrant time on the same input. Chrome silently drops both
        // dialog-open attempts when that happens (confirmed: no
        // `filechooser` event ever fired, real bug found via Playwright).
        onClick={(e) => e.stopPropagation()}
      />
    </button>
  );
}
