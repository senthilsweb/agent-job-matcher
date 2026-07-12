interface ScoreBarProps {
  label: string;
  value: number;
  max: number;
}

// Deliberately not shadcn's Progress primitive — its API assumes a fixed
// 0-100 scale, and required_skills_score's max varies (60 when the
// preferred-skill budget reallocates, per ScoreBreakdown). A plain div bar
// renders each sub-score against its own actual scale, exactly as the
// backend computed it — no re-deriving a percentage against a wrong max.
export function ScoreBar({ label, value, max }: ScoreBarProps) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className="space-y-1">
      <div className="flex items-baseline justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium tabular-nums">
          {value}/{max}
        </span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-brand-600 transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
