import { Briefcase } from "lucide-react";
import { Icon } from "@iconify/react";
import { cn } from "@/lib/utils";

// Direct port of privacyshield/frontend/src/components/Sidebar.tsx's
// structure (dark brand-700 rail, collapsible width, fixed-footer GitHub
// link) — borrowed per the owner's explicit UAT direction (2026-07-12)
// rather than reinvented. Only one nav item exists here (this app has one
// job), so there's no tab-switching list, but the chrome — colors, the
// logo tile, the footer — is the same component shape.
export function NavRail({ collapsed }: { collapsed: boolean }) {
  return (
    <aside
      className={cn(
        "hidden shrink-0 flex-col border-r border-brand-900/30 bg-brand-700 text-brand-50 transition-[width] duration-200 ease-out lg:flex",
        collapsed ? "w-16" : "w-60"
      )}
    >
      <div className={cn("flex h-16 items-center", collapsed ? "justify-center px-0" : "gap-2.5 px-5")}>
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-800/50">
          <Briefcase className="h-5 w-5 text-white" />
        </div>
        {!collapsed && (
          <div className="flex flex-col leading-tight">
            <span className="text-sm font-semibold text-white">Job Matcher</span>
            <span className="text-[11px] text-brand-200">Playground</span>
          </div>
        )}
      </div>

      <nav className="mt-2 flex-1 overflow-y-auto px-2">
        {!collapsed && (
          <p className="px-3 pb-1 pt-2 text-[10px] font-semibold uppercase tracking-wider text-brand-300">
            Workflow
          </p>
        )}
        <ul className="space-y-1">
          <li>
            <div
              className={cn(
                "flex w-full items-center rounded-lg bg-brand-800 text-sm font-medium text-white shadow-sm",
                collapsed ? "justify-center px-0 py-2" : "gap-3 px-3 py-2"
              )}
            >
              <Briefcase className="h-5 w-5 shrink-0" />
              {!collapsed && <span className="flex-1 text-left">Analyze</span>}
            </div>
          </li>
        </ul>

        {!collapsed && <ScoringGuide />}
      </nav>

      <div className="border-t border-brand-900/40 p-2">
        <a
          href="https://github.com/senthilsweb/agent-job-matcher"
          target="_blank"
          rel="noreferrer"
          title="GitHub"
          className={cn(
            "flex items-center rounded-lg text-sm text-brand-100 hover:bg-brand-800/60 hover:text-white",
            collapsed ? "justify-center px-0 py-2" : "gap-3 px-3 py-2"
          )}
        >
          <Icon icon="mdi:github" className="h-5 w-5 shrink-0" />
          {!collapsed && <span>GitHub</span>}
        </a>
      </div>
    </aside>
  );
}

// The band boundaries computed in backend/job_matcher/scoring.py's
// match_band_for() (>=80 / >=65 / >=50 / >=35 / else) — kept in sync by
// hand, same convention as lib/types.ts's MATCH_STATUS_CLASSES, whose
// colors these dots mirror exactly. Fills the nav rail's otherwise-empty
// space below the single "Analyze" item with the one piece of context a
// first-time visitor actually needs: what the score means.
const SCORING_BANDS: { label: string; range: string; dot: string }[] = [
  { label: "Strong match", range: "80-100", dot: "bg-emerald-500" },
  { label: "Good match", range: "65-79", dot: "bg-lime-500" },
  { label: "Moderate match", range: "50-64", dot: "bg-amber-500" },
  { label: "Weak match", range: "35-49", dot: "bg-orange-500" },
  { label: "No match", range: "0-34", dot: "bg-red-500" },
];

function ScoringGuide() {
  return (
    <div className="mt-6">
      <p className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-brand-300">
        Scoring guide
      </p>
      <ul className="space-y-1.5 px-3">
        {SCORING_BANDS.map((band) => (
          <li key={band.label} className="flex items-center gap-2 text-xs text-brand-100">
            <span className={cn("size-2 shrink-0 rounded-full", band.dot)} />
            <span className="flex-1">{band.label}</span>
            <span className="tabular-nums text-brand-300">{band.range}</span>
          </li>
        ))}
      </ul>
      <p className="mt-3 px-3 text-[10px] leading-relaxed text-brand-300">
        Required 40 (or 60 if no preferred skills) / Preferred 20 /
        Experience 20 / Domain 20 — computed by code, never the LLM.
      </p>
    </div>
  );
}
