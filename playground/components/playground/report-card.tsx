import {
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScoreBar } from "@/components/playground/score-bar";
import { CoverLetterSection } from "@/components/playground/cover-letter-section";
import {
  JobOutcome,
  MATCH_STATUS_CLASSES,
  MATCH_STATUS_LABEL,
} from "@/lib/types";
import { AlertTriangle, CheckCircle2, ChevronsUpDown, XCircle } from "lucide-react";

function SkillPill({ skill, matched }: { skill: string; matched: boolean }) {
  return (
    <li className="flex items-start gap-1.5 text-xs">
      {matched ? (
        <CheckCircle2 className="mt-0.5 size-3.5 shrink-0 text-emerald-600" />
      ) : (
        <XCircle className="mt-0.5 size-3.5 shrink-0 text-muted-foreground/50" />
      )}
      <span className={matched ? "" : "text-muted-foreground"}>{skill}</span>
    </li>
  );
}

export function ReportCard({ outcome, value }: { outcome: JobOutcome; value: string }) {
  if (outcome.fetch_status === "failed") {
    return (
      <AccordionItem
        value={value}
        className="rounded-xl border bg-card px-4 shadow-sm"
      >
        <AccordionTrigger className="hover:no-underline">
          <div className="flex min-w-0 flex-1 items-center gap-3 py-1">
            <AlertTriangle className="size-4 shrink-0 text-destructive" />
            <span className="min-w-0 flex-1 truncate text-sm font-medium">
              {outcome.job_source}
            </span>
            <Badge variant="destructive">Fetch failed</Badge>
          </div>
        </AccordionTrigger>
        <AccordionContent>
          <p className="text-sm text-muted-foreground">{outcome.reason}</p>
        </AccordionContent>
      </AccordionItem>
    );
  }

  const { analysis, score_breakdown, match_status, recommendation } = outcome;

  return (
    <AccordionItem
      value={value}
      className="rounded-xl border bg-card px-4 shadow-sm transition-shadow hover:shadow-md"
    >
      <AccordionTrigger className="-mx-2 rounded-lg px-2 hover:bg-accent/40 hover:underline-offset-0 hover:no-underline [&>svg]:self-center">
        <div className="grid w-full min-w-0 flex-1 grid-cols-[1fr_auto] items-start gap-x-4 gap-y-3 py-1.5 pr-2">
          <div className="col-span-2 flex min-w-0 items-center gap-2 sm:col-span-1">
            <span className="min-w-0 truncate text-sm font-semibold">
              {analysis.job_title}
            </span>
          </div>
          <div className="row-start-1 flex items-center gap-2 sm:col-start-2 sm:row-start-1">
            <Badge className={MATCH_STATUS_CLASSES[match_status]}>
              {MATCH_STATUS_LABEL[match_status]}
            </Badge>
            <span className="text-lg font-bold tabular-nums text-brand-700">
              {score_breakdown.total_score}
              <span className="text-xs font-normal text-muted-foreground">/100</span>
            </span>
          </div>
          {analysis.company_name && (
            <span className="col-span-2 -mt-2 truncate text-xs text-muted-foreground sm:col-span-1">
              {analysis.company_name}
            </span>
          )}
          <div className="col-span-2 grid grid-cols-2 gap-x-4 gap-y-2 sm:col-span-2">
            <ScoreBar
              label="Required"
              value={score_breakdown.required_skills_score}
              // The backend reallocates the preferred-skill budget (20pts)
              // into required's max when a job lists no preferred skills
              // (scoring.py) — reflect the actual scale, not a fixed 40.
              max={analysis.preferred_skills.length === 0 ? 60 : 40}
            />
            <ScoreBar
              label="Preferred"
              value={score_breakdown.preferred_skills_score}
              max={20}
            />
            <ScoreBar label="Experience" value={score_breakdown.experience_score} max={20} />
            <ScoreBar label="Domain" value={score_breakdown.domain_score} max={20} />
          </div>
          <div className="col-span-2 -mb-1 flex items-center gap-1 text-[11px] text-muted-foreground/70 sm:col-span-2">
            <ChevronsUpDown className="size-3" />
            Click to expand full report
          </div>
        </div>
      </AccordionTrigger>

      <AccordionContent>
        <Separator className="mb-3" />
        <div className="space-y-4">
          <p className="text-sm">{analysis.summary}</p>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <h4 className="mb-1.5 text-xs font-semibold tracking-wide text-brand-700 uppercase">
                Required skills
              </h4>
              <ul className="space-y-1">
                {analysis.required_skills.map((s, i) => (
                  <SkillPill key={i} skill={s.skill} matched={s.matched} />
                ))}
              </ul>
            </div>
            <div>
              <h4 className="mb-1.5 text-xs font-semibold tracking-wide text-brand-700 uppercase">
                Preferred skills
              </h4>
              <ul className="space-y-1">
                {analysis.preferred_skills.map((s, i) => (
                  <SkillPill key={i} skill={s.skill} matched={s.matched} />
                ))}
              </ul>
            </div>
          </div>

          {analysis.gaps.length > 0 && (
            <div>
              <h4 className="mb-1.5 text-xs font-semibold tracking-wide text-brand-700 uppercase">
                Gaps
              </h4>
              <ul className="list-inside list-disc space-y-0.5 text-xs text-muted-foreground">
                {analysis.gaps.map((g, i) => (
                  <li key={i}>{g}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="rounded-lg bg-accent/50 px-3 py-2 text-xs text-accent-foreground">
            <span className="font-semibold">Recommendation: </span>
            {recommendation}
          </div>

          <CoverLetterSection text={outcome.cover_letter_text} />
        </div>
      </AccordionContent>
    </AccordionItem>
  );
}
