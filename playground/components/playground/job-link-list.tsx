"use client";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, X } from "lucide-react";

interface JobLinkListProps {
  links: string[];
  onChange: (links: string[]) => void;
}

export function JobLinkList({ links, onChange }: JobLinkListProps) {
  const update = (index: number, value: string) => {
    const next = [...links];
    next[index] = value;
    onChange(next);
  };

  const addRow = () => onChange([...links, ""]);

  const removeRow = (index: number) => {
    if (links.length === 1) {
      onChange([""]);
      return;
    }
    onChange(links.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-2">
      {links.map((link, index) => {
        const isLast = index === links.length - 1;
        return (
          <div key={index} className="flex items-center gap-1.5">
            <Input
              value={link}
              onChange={(e) => update(index, e.target.value)}
              placeholder="https://careers.example.com/job/123"
              className="text-sm"
            />
            {links.length > 1 && (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="size-8 shrink-0 text-muted-foreground hover:text-destructive"
                onClick={() => removeRow(index)}
                aria-label="Remove job link"
              >
                <X className="size-4" />
              </Button>
            )}
            {/* Placed directly next to the last link's input, not as a
                separate block below (owner UAT feedback, 2026-07-12) —
                Slack's green accent (#2EB67D) for the add action, square
                corners rather than the rest of the app's rounded controls. */}
            {isLast && (
              <Button
                type="button"
                size="icon"
                className="size-8 shrink-0 rounded-none bg-slack-green text-white hover:bg-slack-green-dark"
                onClick={addRow}
                aria-label="Add another job"
              >
                <Plus className="size-4" />
              </Button>
            )}
          </div>
        );
      })}
    </div>
  );
}
