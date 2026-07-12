"use client";

import { useState } from "react";
import {
  Collapsible,
  CollapsibleTrigger,
  CollapsibleContent,
} from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";
import { ChevronDown, Copy, Check, Mail } from "lucide-react";

// Collapsed by default (keeps the report compact) — matches
// privacyshield's Workspace.tsx OutputCard copy-button pattern: icon
// swaps to a checkmark for ~1.5s as the confirmation, no toast library.
export function CoverLetterSection({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard permission denied or unavailable — button simply stays
      // in its un-copied state, no crash.
    }
  };

  return (
    <Collapsible className="rounded-lg border">
      <div className="flex items-center justify-between gap-2 px-3 py-2">
        <CollapsibleTrigger className="group/cl flex flex-1 items-center gap-2 text-left text-xs font-semibold tracking-wide text-brand-700 uppercase outline-none">
          <Mail className="size-3.5" />
          Cover letter
          <ChevronDown className="ml-auto size-4 text-muted-foreground transition-transform group-data-[panel-open]/cl:rotate-180" />
        </CollapsibleTrigger>
        <Button
          type="button"
          variant="ghost"
          size="icon-sm"
          className="shrink-0"
          onClick={handleCopy}
          aria-label="Copy cover letter"
        >
          {copied ? (
            <Check className="size-3.5 text-emerald-600" />
          ) : (
            <Copy className="size-3.5" />
          )}
        </Button>
      </div>
      <CollapsibleContent className="border-t px-3 py-3">
        <p className="whitespace-pre-wrap text-xs leading-relaxed text-muted-foreground">
          {text}
        </p>
      </CollapsibleContent>
    </Collapsible>
  );
}
