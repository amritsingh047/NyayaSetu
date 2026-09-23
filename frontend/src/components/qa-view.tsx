'use client';

import { useState, useRef, useEffect } from 'react';
import { askQuestion } from '@/lib/api';
import { ConfidenceIndicator } from './confidence-indicator';
import { SourceCitation } from './source-citation';
import { Send, Loader2, AlertTriangle, MessageSquare, ShieldAlert } from 'lucide-react';

interface QAMessage {
  id: string;
  question: string;
  answer: string;
  sourceExcerpts: string[];
  confidence: number;
  isOutOfScope: boolean;
}

interface Props {
  documentId: string;
}

const STARTER_QUESTIONS = [
  'What are my primary obligations under this agreement?',
  'What is the term duration and how can either party terminate?',
  'Are there any penalties, fees, or automatic renewal clauses?',
  'How is confidential information protected?',
];

export function QAView({ documentId }: Props) {
  const [messages, setMessages] = useState<QAMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function handleAsk(question?: string) {
    const q = question || input.trim();
    if (!q || isLoading) return;
    setInput('');
    setIsLoading(true);

    try {
      const result = await askQuestion(documentId, q);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          question: q,
          answer: result.answer,
          sourceExcerpts: result.source_excerpts || [],
          confidence: result.confidence ?? 0.85,
          isOutOfScope: result.is_out_of_scope || false,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          question: q,
          answer: 'Unable to process query. Please verify that your backend server is active and try again.',
          sourceExcerpts: [],
          confidence: 0,
          isOutOfScope: false,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-[520px]">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        {messages.length === 0 && (
          <div className="py-4 space-y-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Suggested questions grounded in your document:
            </p>
            <div className="space-y-2">
              {STARTER_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => handleAsk(q)}
                  className="w-full text-left text-xs bg-muted/50 hover:bg-muted border border-border/60 rounded-xl px-3.5 py-2.5 text-foreground transition-colors flex items-center justify-between group"
                >
                  <span>{q}</span>
                  <span className="text-primary opacity-0 group-hover:opacity-100 transition-opacity text-[11px] font-medium">Ask →</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className="space-y-2">
            {/* User Query */}
            <div className="flex justify-end">
              <div className="bg-primary text-primary-foreground rounded-2xl rounded-tr-sm px-4 py-2.5 max-w-[85%] text-xs font-medium shadow-sm">
                {msg.question}
              </div>
            </div>

            {/* AI Grounded Answer */}
            <div className="flex gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-primary/10 text-primary flex items-center justify-center flex-shrink-0 mt-0.5">
                <MessageSquare className="h-3.5 w-3.5" />
              </div>
              <div className="flex-1 bg-muted/40 border border-border rounded-2xl rounded-tl-sm px-4 py-3 space-y-2.5 text-xs">
                {msg.isOutOfScope && (
                  <div className="flex items-center gap-1.5 text-amber-700 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 p-2 rounded-lg font-medium">
                    <ShieldAlert className="h-4 w-4 flex-shrink-0 text-amber-600" />
                    <span>Out of scope for document Q&A — professional legal counsel recommended.</span>
                  </div>
                )}

                <p className="text-foreground leading-relaxed text-xs">{msg.answer}</p>

                {msg.confidence > 0 && (
                  <div className="pt-1">
                    <ConfidenceIndicator score={msg.confidence} />
                  </div>
                )}

                {msg.sourceExcerpts?.map((excerpt, i) => (
                  <SourceCitation key={i} excerpt={excerpt} />
                ))}

                <p className="text-[10px] text-muted-foreground pt-1 border-t border-border/50">
                  ⚠️ Grounded in document text. Does not constitute binding legal counsel.
                </p>
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-2.5 items-center text-xs text-muted-foreground py-2">
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
            <span>Searching document chunks and formulating answer...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input box */}
      <div className="flex gap-2 border-t border-border pt-3 mt-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleAsk()}
          placeholder="Ask a question about this contract..."
          className="flex-1 border border-input rounded-xl px-3.5 py-2 text-xs bg-background focus:outline-none focus:ring-2 focus:ring-ring"
          disabled={isLoading}
        />
        <button
          onClick={() => handleAsk()}
          disabled={!input.trim() || isLoading}
          className="bg-primary text-primary-foreground rounded-xl px-4 py-2 hover:opacity-90 disabled:opacity-50 transition-opacity flex items-center justify-center"
        >
          <Send className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}
