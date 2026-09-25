'use client';

import { useState } from 'react';
import { DocumentUploader } from '@/components/document-uploader';
import { DisclaimerModal } from '@/components/disclaimer-modal';
import { SummaryPanel } from '@/components/summary-panel';
import { ClauseHighlightList } from '@/components/clause-highlight';
import { QAView } from '@/components/qa-view';
import { ChecklistPanel } from '@/components/checklist-panel';
import { GlossaryPanel } from '@/components/glossary-panel';
import { useDocumentStore } from '@/store/document-store';
import {
  Scale,
  FileText,
  MessageSquare,
  CheckSquare,
  Layers,
  BookMarked,
  ShieldCheck,
  Landmark,
  PhoneCall,
  Search,
} from 'lucide-react';

const TABS = [
  { id: 'summary', label: 'Plain Summary', icon: FileText },
  { id: 'clauses', label: 'Clause Risk & Red Flags', icon: Layers },
  { id: 'qa', label: 'Contextual Q&A', icon: MessageSquare },
  { id: 'checklist', label: 'Tasks Before Advocate', icon: CheckSquare },
  { id: 'glossary', label: 'Indian Legal Glossary', icon: BookMarked },
] as const;

type TabId = (typeof TABS)[number]['id'];

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<TabId>('summary');
  const { currentDocument } = useDocumentStore();

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Top Header */}
      <header className="border-b border-border bg-card/90 backdrop-blur sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-primary text-primary-foreground flex items-center justify-center font-bold shadow-sm">
              <Scale className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight text-foreground">NyayaSetu</span>
                <span className="text-[11px] font-bold text-primary font-serif">न्याय सेतु</span>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">
                  Legal Bridge (India MVP)
                </span>
              </div>
              <p className="text-[10px] text-muted-foreground hidden sm:block">
                AI-Assisted Legal Information & Document Comprehension Platform
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <a
              href="https://nalsa.gov.in"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-lg border border-primary/20 bg-primary/5 text-primary text-[11px] font-semibold hover:bg-primary/10 transition-colors"
            >
              <PhoneCall className="h-3 w-3" />
              <span>Free Legal Aid Helpline: 15100 (NALSA)</span>
            </a>
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-amber-200/80 bg-amber-50/70 dark:bg-amber-950/20 dark:border-amber-800 text-[10px] text-amber-800 dark:text-amber-300 font-medium">
              <ShieldCheck className="h-3.5 w-3.5 text-amber-600 flex-shrink-0" />
              <span>Information Only (Advocates Act, 1961)</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!currentDocument ? (
          /* Empty / Landing State */
          <div className="max-w-3xl mx-auto space-y-8 py-4">
            <div className="text-center space-y-3">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
                <Landmark className="h-3.5 w-3.5" />
                <span>Anchored in Indian Constitutional, Statutory & Regulatory Law</span>
              </div>
              <h1 className="text-3xl sm:text-4xl font-extrabold text-foreground tracking-tight">
                Understand agreements, policies, and Indian law in plain English.
              </h1>
              <p className="text-muted-foreground text-xs sm:text-sm max-w-2xl mx-auto leading-relaxed">
                Upload commercial supply agreements, leases, NDAs, or employment contracts. NyayaSetu highlights
                problematic clauses (e.g. Section 27 non-compete voidness, uncapped liabilities, GST non-compliance),
                extracts checklists before consulting an Advocate, and answers questions strictly anchored in official statutes.
              </p>
            </div>

            <DocumentUploader />

            {/* Feature Highlights Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 pt-2 text-xs">
              <div className="border border-border rounded-xl p-4 bg-card/60 space-y-1.5 shadow-sm">
                <div className="font-bold text-foreground flex items-center gap-1.5 text-xs">
                  <FileText className="h-4 w-4 text-primary" /> Plain-Language Summaries
                </div>
                <p className="text-muted-foreground text-[11px] leading-relaxed">
                  Translates Latin maxims (*mutatis mutandis*, *force majeure*) into everyday language with key obligations highlighted.
                </p>
              </div>

              <div className="border border-border rounded-xl p-4 bg-card/60 space-y-1.5 shadow-sm">
                <div className="font-bold text-foreground flex items-center gap-1.5 text-xs">
                  <Layers className="h-4 w-4 text-primary" /> Indian Legal Risk Detection
                </div>
                <p className="text-muted-foreground text-[11px] leading-relaxed">
                  Flags agreements in restraint of trade (Sec 27 Indian Contract Act), penalty traps (Sec 74), and DPDP consent omissions.
                </p>
              </div>

              <div className="border border-border rounded-xl p-4 bg-card/60 space-y-1.5 shadow-sm">
                <div className="font-bold text-foreground flex items-center gap-1.5 text-xs">
                  <CheckSquare className="h-4 w-4 text-primary" /> Pre-Advocate Dossier
                </div>
                <p className="text-muted-foreground text-[11px] leading-relaxed">
                  Generates an actionable checklist of proof, tax invoices, and questions to review before consulting a licensed Advocate.
                </p>
              </div>
            </div>
          </div>
        ) : (
          /* Active Document Analysis Workspace */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Main Analysis Column (8 cols) */}
            <div className="lg:col-span-8 space-y-4">
              {/* Document Overview Bar */}
              <div className="bg-card border border-border rounded-xl p-4 flex items-center justify-between shadow-sm">
                <div>
                  <h2 className="font-bold text-foreground text-sm sm:text-base">{currentDocument.title}</h2>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5 flex-wrap">
                    <span className="capitalize font-semibold text-primary">{currentDocument.doc_type}</span>
                    <span>•</span>
                    <span>Jurisdiction: {currentDocument.jurisdiction}</span>
                    <span>•</span>
                    <span>{currentDocument.page_count ?? 1} pg</span>
                    {currentDocument.word_count && (
                      <>
                        <span>•</span>
                        <span>{currentDocument.word_count.toLocaleString()} words</span>
                      </>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-green-100 text-green-800 dark:bg-green-950/40 dark:text-green-300 border border-green-200">
                    Analysis Ready
                  </span>
                </div>
              </div>

              {/* Tabbed Analysis Container */}
              <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
                {/* Tab Navigation */}
                <div className="flex border-b border-border bg-muted/20 overflow-x-auto">
                  {TABS.map(({ id, label, icon: Icon }) => (
                    <button
                      key={id}
                      onClick={() => setActiveTab(id)}
                      className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold tracking-wide whitespace-nowrap transition-colors border-b-2 ${
                        activeTab === id
                          ? 'border-primary text-primary bg-card'
                          : 'border-transparent text-muted-foreground hover:text-foreground hover:bg-muted/40'
                      }`}
                    >
                      <Icon className="h-4 w-4" />
                      {label}
                    </button>
                  ))}
                </div>

                {/* Tab Panels */}
                <div className="p-5">
                  {activeTab === 'summary' && <SummaryPanel documentId={currentDocument.id} />}
                  {activeTab === 'clauses' && <ClauseHighlightList documentId={currentDocument.id} />}
                  {activeTab === 'qa' && <QAView documentId={currentDocument.id} />}
                  {activeTab === 'checklist' && <ChecklistPanel documentId={currentDocument.id} />}
                  {activeTab === 'glossary' && <GlossaryPanel documentId={currentDocument.id} />}
                </div>
              </div>
            </div>

            {/* Side Column (4 cols) */}
            <div className="lg:col-span-4 space-y-4">
              <DocumentUploader compact />

              {/* Indian Statutory Quick Links Card */}
              <div className="border border-border rounded-xl p-4 bg-card/80 space-y-3 text-xs shadow-sm">
                <div className="flex items-center gap-2 font-bold text-foreground uppercase tracking-wider text-[11px]">
                  <Landmark className="h-3.5 w-3.5 text-primary" />
                  <span>Governing Statutory References</span>
                </div>
                <div className="space-y-2 text-[11px] text-muted-foreground">
                  <p>
                    • <strong>Indian Contract Act, 1872:</strong> Sec 27 (restraint of trade void) & Sec 74 (liquidated damages).
                  </p>
                  <p>
                    • <strong>CGST Act, 2017:</strong> Sec 16 (ITC eligibility) & Rule 48(4) (mandatory e-invoicing).
                  </p>
                  <p>
                    • <strong>DPDP Act, 2023:</strong> Sec 5 & 6 (notice & free consent) & Sec 33 (breach penalties).
                  </p>
                  <p>
                    • <strong>FSS Act, 2006:</strong> Sec 31 mandatory licensing for food operators.
                  </p>
                </div>
              </div>

              {/* Bar Council & NALSA Legal Aid Escalation Card */}
              <div className="disclaimer-banner text-xs space-y-2">
                <p className="font-bold text-amber-900 dark:text-amber-200">⚖️ Advocate Consultation & Legal Aid</p>
                <p className="leading-relaxed text-[11px]">
                  NyayaSetu provides educational document comprehension. For disputes or litigation representation in Indian courts, consult an Advocate enrolled with the State Bar Council.
                </p>
                <div className="pt-1">
                  <a
                    href="https://nalsa.gov.in"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-[11px] font-bold text-primary underline"
                  >
                    Find Free Legal Aid on NALSA Portal →
                  </a>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Global Disclaimer Modal */}
      <DisclaimerModal />
    </div>
  );
}
