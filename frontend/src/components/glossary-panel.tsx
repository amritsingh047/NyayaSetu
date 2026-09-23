'use client';

import { useState } from 'react';
import { BookMarked, Search, Landmark } from 'lucide-react';

interface GlossaryTerm {
  term: string;
  hindi_term?: string;
  definition_generic: string;
  definition_indian_law: string;
  act_citation?: string;
}

const INDIAN_LEGAL_GLOSSARY: GlossaryTerm[] = [
  {
    term: 'Vakalatnama',
    hindi_term: 'वकालतनामा',
    definition_generic: 'A written document submitted to a court authorizing an advocate to represent a client.',
    definition_indian_law: 'Under Section 30 of the Advocates Act, 1961 and the Code of Civil Procedure (Order III), a Vakalatnama formally appoints an enrolled Advocate to plead, act, and file petitions on your behalf.',
    act_citation: 'Advocates Act, 1961 & CPC Order III',
  },
  {
    term: 'Restraint of Trade',
    hindi_term: 'व्यापार में अवरोध',
    definition_generic: 'A contract clause that prevents someone from practicing their profession or business.',
    definition_indian_law: 'Section 27 of the Indian Contract Act, 1872 states that any agreement restraining someone from exercising a lawful profession, trade, or business is to that extent VOID. Post-employment non-compete clauses are unenforceable in Indian courts.',
    act_citation: 'Indian Contract Act, 1872 (Sec. 27)',
  },
  {
    term: 'Input Tax Credit (ITC)',
    hindi_term: 'इनपुट टैक्स क्रेडिट',
    definition_generic: 'Credit claimed for taxes paid on business purchases to offset taxes due on sales.',
    definition_indian_law: 'Under Section 16 of the CGST Act, 2017, a buyer can only claim ITC if the supplier has uploaded the invoice in GSTR-1 (reflected in GSTR-2B) and payment is made within 180 days.',
    act_citation: 'CGST Act, 2017 (Sec. 16)',
  },
  {
    term: 'Data Fiduciary',
    hindi_term: 'डेटा फिड्यूशरी / डेटा न्यासी',
    definition_generic: 'An entity or company that decides the purpose and means of processing personal data.',
    definition_indian_law: 'Under the Digital Personal Data Protection Act, 2023 (DPDP), Data Fiduciaries must give clear notice, obtain unambiguous affirmative consent, and ensure technical safeguards. Penalties for data breaches reach up to ₹250 Crore.',
    act_citation: 'DPDP Act, 2023 (Sec. 2(i) & Sec. 8)',
  },
  {
    term: 'Liquidated Damages vs. Penalty',
    hindi_term: 'परिनिर्धारित क्षतिपूर्ति बनाम शास्ति',
    definition_generic: 'Pre-agreed financial amounts payable in the event of contract breach.',
    definition_indian_law: 'Under Indian Contract Act (Section 74) as affirmed in Kailash Nath Associates v. DDA, Indian courts do not enforce penal amounts and award only reasonable compensation based on actual damage, unless proving loss is genuinely impossible.',
    act_citation: 'Indian Contract Act, 1872 (Sec. 74)',
  },
  {
    term: 'Arbitration (Madhyasthata)',
    hindi_term: 'मध्यस्थता',
    definition_generic: 'Settling commercial disputes outside court through an independent arbitrator.',
    definition_indian_law: 'Governed by the Arbitration and Conciliation Act, 1996. The arbitral award holds the same enforceability as a civil court decree. The seat of arbitration dictates the supervising High Court.',
    act_citation: 'Arbitration & Conciliation Act, 1996 (Sec. 7)',
  },
  {
    term: 'Unfair Contract',
    hindi_term: 'अनुचित अनुबंध',
    definition_generic: 'A contract imposing significantly one-sided or oppressive terms on a weaker party.',
    definition_indian_law: 'Defined under Section 2(46) of the Consumer Protection Act, 2019. Terms such as excessive security deposits, unilateral termination without reasonable cause, or non-refundable full advances can be declared null and void by Consumer Commissions.',
    act_citation: 'Consumer Protection Act, 2019 (Sec. 2(46))',
  },
  {
    term: 'Food Business Operator (FBO)',
    hindi_term: 'खाद्य व्यवसाय संचालक',
    definition_generic: 'Any individual or entity carrying out any activity relating to food manufacturing, processing, storage, or distribution.',
    definition_indian_law: 'Section 31 of the Food Safety and Standards Act (FSSA), 2006 mandates every FBO to obtain an FSSAI License or Registration. Operating without one attracts imprisonment up to 6 months and fines up to ₹5 Lakhs (Sec. 63).',
    act_citation: 'FSS Act, 2006 (Sec. 31 & Sec. 63)',
  },
  {
    term: 'Quality Control Order (QCO)',
    hindi_term: 'गुणवत्ता नियंत्रण आदेश',
    definition_generic: 'Government-mandated technical standards for manufactured or imported products.',
    definition_indian_law: 'Issued by the Ministry of Textiles and Bureau of Indian Standards (BIS) for technical textiles, synthetic fibres, and geotextiles. Products must bear the ISI Mark; contracts cannot contract out of mandatory statutory QCOs.',
    act_citation: 'Textiles Committee Act, 1963 / BIS Act, 2016',
  },
];

interface Props {
  documentId: string;
}

export function GlossaryPanel({ documentId }: Props) {
  const [searchTerm, setSearchTerm] = useState('');
  const [terms] = useState<GlossaryTerm[]>(INDIAN_LEGAL_GLOSSARY);

  const filtered = terms.filter(
    (t) =>
      t.term.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (t.hindi_term && t.hindi_term.includes(searchTerm)) ||
      t.definition_generic.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.definition_indian_law.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search Indian legal terms (e.g. Vakalatnama, ITC, Restraint of Trade, DPDP)..."
          className="w-full pl-9 pr-4 py-2 border border-input rounded-xl text-xs bg-background focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>

      <div className="space-y-3">
        {filtered.map((item, idx) => (
          <div key={idx} className="bg-card border border-border rounded-xl p-4 space-y-2.5 shadow-sm hover:border-primary/40 transition-colors">
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                <BookMarked className="h-4 w-4 text-primary" />
                <h4 className="font-bold text-foreground text-xs sm:text-sm">
                  {item.term} {item.hindi_term && <span className="text-muted-foreground font-normal">({item.hindi_term})</span>}
                </h4>
              </div>
              {item.act_citation && (
                <span className="text-[10px] font-semibold bg-primary/10 text-primary border border-primary/20 px-2 py-0.5 rounded-full flex-shrink-0">
                  {item.act_citation}
                </span>
              )}
            </div>

            <p className="text-xs text-muted-foreground leading-relaxed">
              <strong className="text-foreground">Plain Meaning:</strong> {item.definition_generic}
            </p>

            <div className="bg-primary/5 border border-primary/20 rounded-lg p-3 text-xs text-foreground leading-relaxed">
              <div className="flex items-center gap-1.5 font-bold text-primary mb-1">
                <Landmark className="h-3 w-3" />
                <span>Under Indian Statutory Law & Precedents:</span>
              </div>
              <span>{item.definition_indian_law}</span>
            </div>
          </div>
        ))}

        {filtered.length === 0 && (
          <p className="text-center text-xs text-muted-foreground py-6">
            No terms found matching "{searchTerm}".
          </p>
        )}
      </div>

      <div className="disclaimer-banner text-xs">
        ⚠️ Definitions explain Indian statutory provisions and general principles for non-lawyers. They do not constitute formal legal counsel.
      </div>
    </div>
  );
}
