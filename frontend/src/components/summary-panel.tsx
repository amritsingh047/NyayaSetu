'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { generateSummary } from '@/lib/api';
import { ConfidenceIndicator } from './confidence-indicator';
import { SourceCitation } from './source-citation';
import { Loader2, AlertTriangle, BookOpen, FileCheck } from 'lucide-react';

interface Props {
  documentId: string;
}

const SUMMARY_MODES = [
  { value: 'brief', label: 'Quick Overview' },
  { value: 'detailed', label: 'Detailed Breakdown' },
];

export function SummaryPanel({ documentId }: Props) {
  const [summaryMode, setSummaryMode] = useState('brief');

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['summary', documentId, summaryMode],
    queryFn: () => generateSummary(documentId, summaryMode),
    staleTime: 10 * 60 * 1000,
  });

  return (
    <div className="space-y-4">
      {/* Mode Selector */}
      <div className="flex items-center justify-between pb-2 border-b border-border">
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-primary" />
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Summary Depth:</span>
        </div>
        <div className="flex gap-1">
          {SUMMARY_MODES.map((m) => (
            <button
              key={m.value}
              onClick={() => setSummaryMode(m.value)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                summaryMode === m.value
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading && (
        <div className="flex items-center gap-2 text-muted-foreground py-12 justify-center">
          <Loader2 className="h-5 w-5 animate-spin text-primary" />
          Generating plain-language summary...
        </div>
      )}

      {error && (
        <div className="text-destructive text-sm bg-destructive/10 rounded-lg p-3">
          Failed to generate summary.{' '}
          <button onClick={() => refetch()} className="underline font-semibold">
            Retry
          </button>
        </div>
      )}

      {data && (
        <div className="space-y-4">
          {/* Main Purpose Card */}
          <div className="bg-muted/40 border border-border rounded-xl p-4 space-y-2">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <FileCheck className="h-4 w-4 text-primary" />
                <h3 className="font-semibold text-foreground text-sm">Purpose & Scope</h3>
              </div>
              <ConfidenceIndicator score={data.confidence} />
            </div>
            <p className="text-sm text-foreground leading-relaxed">{data.overview}</p>
            {data.document_type_detected && (
              <span className="inline-block text-xs bg-primary/10 text-primary font-medium px-2 py-0.5 rounded">
                Detected: {data.document_type_detected}
              </span>
            )}
          </div>

          {/* Key Points / Sections */}
          {data.key_points?.length > 0 && (
            <div>
              <h3 className="font-semibold text-foreground text-sm mb-3">Key Terms & Obligations</h3>
              <div className="space-y-2.5">
                {data.key_points.map((kp: { point: string; source_excerpt: string; confidence: number }, i: number) => (
                  <div key={i} className="border border-border/80 rounded-lg p-3 bg-card hover:bg-muted/20 transition-colors">
                    <div className="flex gap-2.5 items-start">
                      <span className="w-5 h-5 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center font-bold flex-shrink-0 mt-0.5">
                        {i + 1}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-foreground leading-relaxed">{kp.point}</p>
                        {kp.source_excerpt && <SourceCitation excerpt={kp.source_excerpt} />}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Risks / Notable Concerns */}
          {data.notable_concerns?.length > 0 && (
            <div className="bg-amber-50 dark:bg-amber-950/20 rounded-xl p-4 border border-amber-200 dark:border-amber-800">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="h-4 w-4 text-amber-600" />
                <h3 className="font-semibold text-amber-800 dark:text-amber-300 text-sm">Notable Risks & Red Flags</h3>
              </div>
              <ul className="space-y-1.5">
                {data.notable_concerns.map((concern: string, i: number) => (
                  <li key={i} className="text-xs text-amber-900 dark:text-amber-200 flex gap-2">
                    <span className="text-amber-600 font-bold">•</span>
                    <span>{concern}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Disclaimer */}
          <div className="disclaimer-banner text-xs">
            {data.disclaimer || '⚠️ This summary is informational only and does not constitute formal legal advice.'}
          </div>
        </div>
      )}
    </div>
  );
}
