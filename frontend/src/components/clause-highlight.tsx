'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getClauses } from '@/lib/api';
import { ConfidenceIndicator } from './confidence-indicator';
import { SourceCitation } from './source-citation';
import { Loader2, ChevronRight, X, AlertCircle } from 'lucide-react';

const RISK_CONFIG = {
  high: { label: 'High Risk', badge: 'bg-red-100 text-red-700 dark:bg-red-950/40 dark:text-red-400 border-red-200', border: 'border-l-4 border-l-red-500' },
  medium: { label: 'Medium Risk', badge: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-950/40 dark:text-yellow-400 border-yellow-200', border: 'border-l-4 border-l-yellow-500' },
  low: { label: 'Low Risk', badge: 'bg-green-100 text-green-700 dark:bg-green-950/40 dark:text-green-400 border-green-200', border: 'border-l-4 border-l-green-500' },
};

const CLAUSE_CATEGORIES = ['all', 'obligation', 'right', 'condition', 'definition', 'risk', 'boilerplate'];

interface Clause {
  id: string;
  text: string;
  clause_type: string;
  risk_level: 'high' | 'medium' | 'low';
  explanation?: string;
  confidence?: number;
  source_excerpt?: string;
  party_affected?: string;
  key_obligations?: string[];
}

interface Props {
  documentId: string;
}

export function ClauseHighlightList({ documentId }: Props) {
  const [selectedClause, setSelectedClause] = useState<Clause | null>(null);
  const [filterType, setFilterType] = useState('all');
  const [filterRisk, setFilterRisk] = useState('all');

  const { data: clauses = [], isLoading, error } = useQuery({
    queryKey: ['clauses', documentId],
    queryFn: () => getClauses(documentId),
  });

  const filtered = clauses.filter((c: Clause) => {
    if (filterType !== 'all' && c.clause_type !== filterType) return false;
    if (filterRisk !== 'all' && c.risk_level !== filterRisk) return false;
    return true;
  });

  return (
    <div className="space-y-4">
      {/* Category & Risk Filters */}
      <div className="space-y-2 border-b border-border pb-3">
        <div className="flex gap-1.5 flex-wrap">
          {['all', 'high', 'medium', 'low'].map((risk) => (
            <button
              key={risk}
              onClick={() => setFilterRisk(risk)}
              className={`px-2.5 py-1 rounded-md text-xs font-medium capitalize transition-colors ${
                filterRisk === risk
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              }`}
            >
              {risk === 'all' ? 'All Risk Levels' : `${risk} Risk`}
            </button>
          ))}
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {CLAUSE_CATEGORIES.map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-2.5 py-1 rounded-md text-xs font-medium capitalize transition-colors ${
                filterType === type
                  ? 'bg-secondary text-secondary-foreground font-semibold'
                  : 'bg-muted/50 text-muted-foreground hover:bg-muted'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {isLoading && (
        <div className="flex items-center gap-2 text-muted-foreground py-10 justify-center">
          <Loader2 className="h-5 w-5 animate-spin text-primary" /> Analyzing & classifying clauses...
        </div>
      )}

      {error && (
        <div className="text-destructive text-sm bg-destructive/10 rounded-lg p-3">
          Failed to load clauses.
        </div>
      )}

      {!isLoading && filtered.length === 0 && (
        <p className="text-muted-foreground text-sm text-center py-8">
          No clauses match the current filter selection.
        </p>
      )}

      <div className="space-y-2.5">
        {filtered.map((clause: Clause) => {
          const risk = RISK_CONFIG[clause.risk_level] || RISK_CONFIG.low;
          return (
            <div
              key={clause.id}
              className={`bg-card border border-border rounded-xl p-3.5 ${risk.border} cursor-pointer hover:shadow-sm transition-all`}
              onClick={() => setSelectedClause(clause)}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${risk.badge}`}>
                      {risk.label}
                    </span>
                    <span className="text-xs text-muted-foreground capitalize font-medium">
                      {clause.clause_type}
                    </span>
                  </div>
                  <p className="text-xs text-foreground line-clamp-2 leading-relaxed">
                    {clause.text}
                  </p>
                  {clause.explanation && (
                    <p className="text-xs text-muted-foreground line-clamp-1 italic">
                      "{clause.explanation}"
                    </p>
                  )}
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-2" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Clause Detail Drawer */}
      {selectedClause && (
        <div className="fixed inset-y-0 right-0 w-full max-w-md bg-card border-l border-border shadow-2xl z-50 overflow-y-auto">
          <div className="p-6 space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <div>
                <span className="text-xs text-muted-foreground uppercase font-bold tracking-wider">Clause Details</span>
                <h3 className="font-bold text-foreground text-base capitalize">{selectedClause.clause_type} Clause</h3>
              </div>
              <button
                onClick={() => setSelectedClause(null)}
                className="text-muted-foreground hover:text-foreground p-1 rounded-md"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="flex items-center gap-2">
              <span className={`text-xs font-bold uppercase px-2.5 py-1 rounded-full border ${RISK_CONFIG[selectedClause.risk_level]?.badge}`}>
                {RISK_CONFIG[selectedClause.risk_level]?.label}
              </span>
              {selectedClause.party_affected && (
                <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded-full">
                  Affects: {selectedClause.party_affected}
                </span>
              )}
            </div>

            <div>
              <h4 className="text-xs font-bold text-muted-foreground mb-1 uppercase tracking-wider">Original Text</h4>
              <div className="text-xs bg-muted/60 border border-border rounded-lg p-3 font-mono leading-relaxed max-h-48 overflow-y-auto">
                {selectedClause.text}
              </div>
            </div>

            {selectedClause.explanation && (
              <div className="bg-primary/5 border border-primary/20 rounded-xl p-3.5 space-y-1">
                <h4 className="text-xs font-bold text-primary uppercase tracking-wider">Plain-Language Meaning</h4>
                <p className="text-sm text-foreground leading-relaxed">{selectedClause.explanation}</p>
              </div>
            )}

            {selectedClause.key_obligations && selectedClause.key_obligations.length > 0 && (
              <div>
                <h4 className="text-xs font-bold text-muted-foreground mb-1.5 uppercase tracking-wider">Obligations Extracted</h4>
                <ul className="space-y-1">
                  {selectedClause.key_obligations.map((o, i) => (
                    <li key={i} className="text-xs text-foreground flex gap-2">
                      <span className="text-primary font-bold">•</span>
                      <span>{o}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {selectedClause.confidence !== undefined && (
              <div className="pt-2 border-t border-border">
                <ConfidenceIndicator score={selectedClause.confidence} label="Extraction Confidence" />
              </div>
            )}

            {selectedClause.source_excerpt && (
              <SourceCitation excerpt={selectedClause.source_excerpt} />
            )}

            <div className="disclaimer-banner text-xs">
              <div className="flex items-start gap-1.5">
                <AlertCircle className="h-3.5 w-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
                <span>This explanation is an informational summary, not a legal opinion on enforceability.</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
