'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, Quote } from 'lucide-react';

interface Props {
  excerpt: string;
  pageNum?: number;
}

export function SourceCitation({ excerpt, pageNum }: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="mt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        <Quote className="h-3 w-3" />
        {expanded ? 'Hide' : 'Show'} source excerpt
        {pageNum && ` (p.${pageNum})`}
        {expanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
      </button>
      {expanded && (
        <blockquote className="mt-2 pl-3 border-l-2 border-primary/40 text-xs text-muted-foreground italic">
          "{excerpt}"
        </blockquote>
      )}
    </div>
  );
}
