import { cn } from "@/lib/utils";
import { BackendStatus } from "@/lib/use-backend-status";

const STATUS_STYLE: Record<BackendStatus, string> = {
  checking: "bg-amber-50 text-amber-700 ring-amber-200",
  online: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  offline: "bg-red-50 text-red-700 ring-red-200",
};

const STATUS_DOT: Record<BackendStatus, string> = {
  checking: "bg-amber-500",
  online: "bg-emerald-500",
  offline: "bg-red-500",
};

const STATUS_LABEL: Record<BackendStatus, string> = {
  checking: "Checking backend…",
  online: "Backend online",
  offline: "Backend unreachable",
};

// Mirrors mcp-chat-client's demo header status pill exactly (same three
// states, same shape) — genuinely polls /api/health, not decorative.
export function StatusPill({ status }: { status: BackendStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset",
        STATUS_STYLE[status]
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", STATUS_DOT[status])} />
      {STATUS_LABEL[status]}
    </span>
  );
}
