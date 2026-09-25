'use client';

import { useEffect, useState } from 'react';
import { Scale, AlertTriangle, ExternalLink, ShieldCheck } from 'lucide-react';
import { useDocumentStore } from '@/store/document-store';

export function DisclaimerModal() {
  const { disclaimerAccepted, acceptDisclaimer } = useDocumentStore();
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const accepted = localStorage.getItem('nyayasetu-disclaimer-accepted');
    if (!accepted) setIsOpen(true);
    else acceptDisclaimer();
  }, [acceptDisclaimer]);

  const handleAccept = () => {
    localStorage.setItem('nyayasetu-disclaimer-accepted', 'true');
    acceptDisclaimer();
    setIsOpen(false);
  };

  if (!isOpen || disclaimerAccepted) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-card border border-border rounded-2xl shadow-2xl max-w-lg w-full p-6 space-y-4">
        <div className="flex items-center gap-3 pb-3 border-b border-border">
          <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 flex items-center justify-center flex-shrink-0">
            <AlertTriangle className="h-5 w-5" />
          </div>
          <div>
            <h2 className="font-bold text-foreground text-base">Mandatory Statutory Legal Notice</h2>
            <p className="text-xs text-muted-foreground">Bar Council of India & Advocates Act, 1961 Compliance</p>
          </div>
        </div>

        <div className="space-y-3 text-xs text-foreground/90 leading-relaxed max-h-[60vh] overflow-y-auto pr-1">
          <p className="p-2.5 rounded-lg bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200 font-medium">
            <strong>NyayaSetu is an AI-assisted legal information and document comprehension platform.</strong>{' '}
            It is an educational and informational tool, NOT a licensed Advocate or law firm.
          </p>

          <div className="space-y-2 text-muted-foreground">
            <p>
              • <strong>No Advocate-Client Relationship:</strong> Interacting with this software does not create an advocate-client relationship under the Advocates Act, 1961 or the Bar Council of India Rules.
            </p>
            <p>
              • <strong>Informational Assistance:</strong> Summaries, clause highlights, and answers are generated via automated analysis anchored to Indian statutory texts. They may not reflect the latest judicial rulings or regional amendments.
            </p>
            <p>
              • <strong>Dispute & Litigation Strategy:</strong> This platform programmatically refuses to offer personalized dispute strategy, predict case outcomes, or advise whether you should sue or sign.
            </p>
            <p>
              • <strong>Data Privacy & DPDP:</strong> All documents are processed transiently with automatic redaction of Aadhaar and PAN numbers under a zero-retention policy.
            </p>
          </div>

          <div className="pt-2 border-t border-border space-y-1">
            <p className="font-bold text-foreground">Need Binding Legal Counsel or Free Legal Aid?</p>
            <p className="text-[11px] text-muted-foreground">
              Under the Legal Services Authorities Act, 1987, free legal aid is available to eligible citizens through NALSA:
            </p>
            <div className="flex gap-2 pt-1 flex-wrap">
              <a
                href="https://nalsa.gov.in"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-[11px] text-primary font-semibold hover:underline bg-primary/5 px-2 py-1 rounded"
              >
                NALSA (National Legal Services Authority) <ExternalLink className="h-3 w-3" />
              </a>
              <a
                href="https://www.tele-law.in"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-[11px] text-primary font-semibold hover:underline bg-primary/5 px-2 py-1 rounded"
              >
                Tele-Law Portal (Govt. of India) <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>
        </div>

        <div className="pt-3 border-t border-border flex gap-3">
          <button
            onClick={handleAccept}
            className="w-full bg-primary text-primary-foreground rounded-xl py-2.5 text-xs font-bold hover:opacity-90 transition-opacity shadow-sm flex items-center justify-center gap-2"
          >
            <ShieldCheck className="h-4 w-4" />
            <span>I Understand & Acknowledge (Continue)</span>
          </button>
        </div>
      </div>
    </div>
  );
}
