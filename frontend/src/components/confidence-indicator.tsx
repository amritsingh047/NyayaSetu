'use client';

interface Props {
  score: number; // 0.0 - 1.0
  label?: string;
  showBar?: boolean;
}

export function ConfidenceIndicator({ score, label, showBar = true }: Props) {
  const pct = Math.round(score * 100);
  const color = pct >= 80 ? 'bg-green-500' : pct >= 60 ? 'bg-yellow-500' : 'bg-red-500';
  const textColor = pct >= 80 ? 'text-green-700' : pct >= 60 ? 'text-yellow-700' : 'text-red-700';

  return (
    <div className="flex items-center gap-2">
      {label && <span className="text-xs text-muted-foreground">{label}:</span>}
      <span className={`text-xs font-medium ${textColor}`}>{pct}% confidence</span>
      {showBar && (
        <div className="w-16 h-1.5 bg-muted rounded-full overflow-hidden">
          <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
        </div>
      )}
    </div>
  );
}
