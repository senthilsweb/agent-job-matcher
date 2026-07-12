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

      <nav className="mt-2 flex-1 px-2">
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
              {!collapsed && <span className="flex-1 text-left">Analyze fit</span>}
            </div>
          </li>
        </ul>
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
