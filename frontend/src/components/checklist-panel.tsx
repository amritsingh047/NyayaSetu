'use client';

import { useQuery } from '@tanstack/react-query';
import { generateChecklist } from '@/lib/api';
import { SourceCitation } from './source-citation';
import { Loader2, Clock, CheckCircle, HelpCircle, AlertTriangle, Download } from 'lucide-react';

interface ChecklistItem {
  item: string;
  date_mentioned?: string;
  party?: string;
  severity?: string;
  source_excerpt: string;
}

interface ChecklistData {
  deadlines: ChecklistItem[];
  required_actions: ChecklistItem[];
  optional_decisions: ChecklistItem[];
  red_flags: ChecklistItem[];
  disclaimer: string;
}

interface Props {
  documentId: string;
}

const CATEGORIES = [
  { key: 'red_flags' as const, label: 'High Priority & Red Flags', icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-50 dark:bg-red-950/20 border-red-200' },
  { key: 'deadlines' as const, label: 'Critical Deadlines', icon: Clock, color: 'text-blue-600', bg: 'bg-blue-50 dark:bg-blue-950/20 border-blue-200' },
  { key: 'required_actions' as const, label: 'Required Obligations', icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50 dark:bg-green-950/20 border-green-200' },
  { key: 'optional_decisions' as const, label: 'Optional Decisions & Rights', icon: HelpCircle, color: 'text-purple-600', bg: 'bg-purple-50 dark:bg-purple-950/20 border-purple-200' },
];

export function ChecklistPanel({ documentId }: Props) {
  const { data, isLoading, error, refetch } = useQuery<ChecklistData>({
    queryKey: ['checklist', documentId],
    queryFn: () => generateChecklist(documentId),
    staleTime: 10 * 60 * 1000,
  });

  function exportMarkdown() {
    if (!data) return;
    const lines = ['# LegalLens Document Action Items & Checklist\n'];
    CATEGORIES.forEach(({ key, label }) => {
      const items = data[key] || [];
      if (items.length > 0) {
        lines.push(`## ${label}`);
        items.forEach((item) => {
          lines.push(`- [ ] ${item.item}${item.date_mentioned ? ` (Deadline: ${item.date_mentioned})` : ''}${item.party ? ` [Responsible: ${item.party}]` : ''}`);
        });
        lines.push('');
      }
    });
    lines.push('---');
    lines.push('⚠️ ' + (data.disclaimer || 'Informational only — does not constitute legal advice.'));
    const blob = new Blob([lines.join('\n')], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'legallens-action-checklist.md';
    a.click();
    URL.revokeObjectURL(url);
  }

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-muted-foreground py-10 justify-center">
        <Loader2 className="h-5 w-5 animate-spin text-primary" /> Extracting obligations, deadlines & red flags...
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-destructive text-sm bg-destructive/10 rounded-lg p-3">
        Failed to extract checklist.{' '}
        <button onClick={() => refetch()} className="underline font-semibold">
          Retry
        </button>
      </div>
    );
  }

  if (!data) return null;

  const totalItems = CATEGORIES.reduce((sum, { key }) => sum + (data[key]?.length || 0), 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between pb-2 border-b border-border">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          {totalItems} Action Items Extracted
        </p>
        <button
          onClick={exportMarkdown}
          className="flex items-center gap-1.5 text-xs font-medium text-foreground hover:bg-muted border border-border rounded-lg px-2.5 py-1 transition-colors"
        >
          <Download className="h-3.5 w-3.5" /> Export Checklist (.md)
        </button>
      </div>

      <div className="space-y-3.5">
        {CATEGORIES.map(({ key, label, icon: Icon, color, bg }) => {
          const items = data[key] || [];
          if (items.length === 0) return null;
          return (
            <div key={key} className={`${bg} border rounded-xl p-3.5 space-y-3`}>
              <div className={`flex items-center justify-between ${color}`}>
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4" />
                  <h3 className="font-bold text-xs uppercase tracking-wide">{label}</h3>
                </div>
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-white/60 dark:bg-black/30">
                  {items.length}
                </span>
              </div>

              <div className="space-y-2">
                {items.map((item, i) => (
                  <div key={i} className="bg-card/90 border border-border/80 rounded-lg p-3 text-xs space-y-1">
                    <p className="font-medium text-foreground leading-relaxed">{item.item}</p>
                    <div className="flex items-center gap-3 text-[11px] text-muted-foreground flex-wrap pt-0.5">
                      {item.date_mentioned && (
                        <span>📅 <strong>Due:</strong> {item.date_mentioned}</span>
                      )}
                      {item.party && (
                        <span>👤 <strong>Party:</strong> {item.party}</span>
                      )}
                      {item.severity && (
                        <span className="capitalize font-semibold">⚡ {item.severity}</span>
                      )}
                    </div>
                    {item.source_excerpt && (
                      <SourceCitation excerpt={item.source_excerpt} />
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <div className="disclaimer-banner text-xs">
        {data.disclaimer || '⚠️ This checklist is generated for informational guidance only.'}
      </div>
    </div>
  );
}
