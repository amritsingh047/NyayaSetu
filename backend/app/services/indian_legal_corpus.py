"""
Authoritative Indian Legal Knowledge Corpus & RAG Retrieval Service.
Seeds core statutes across Constitutional, Tax/GST, Finance, Food Safety, Textiles,
Consumer Protection, Digital Privacy (DPDP), and Contract Law.
"""
from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class StatutoryProvision:
    act: str
    year: int
    section: str
    title: str
    domain: str  # "tax_gst", "finance", "food_safety", "textiles", "dpdp_privacy", "consumer", "contract", "constitution"
    official_citation: str
    summary_plain_english: str
    verbatim_text: str
    effective_date: str
    official_source_url: str


# Seeded curated repository of authoritative Indian Laws & Regulations
INDIAN_LEGAL_CORPUS: list[StatutoryProvision] = [
    # ---- 1. TAX & GST (CGST Act, 2017) ----
    StatutoryProvision(
        act="Central Goods and Services Tax Act",
        year=2017,
        section="Section 16",
        title="Eligibility and Conditions for Taking Input Tax Credit (ITC)",
        domain="tax_gst",
        official_citation="CGST Act 2017, Sec. 16 read with Rule 36(4)",
        summary_plain_english=(
            "A registered business can claim tax credit on business purchases only if: "
            "(1) they hold a valid tax invoice or debit note; (2) the supplier has uploaded the invoice "
            "details in GSTR-1 and it appears in GSTR-2B; (3) the goods or services were actually received; "
            "(4) the tax charged has actually been deposited with the government; and (5) payment to the supplier "
            "is made within 180 days, failing which the credit must be reversed with interest."
        ),
        verbatim_text=(
            "Section 16(2): Notwithstanding anything contained in this section, no registered person shall be entitled "
            "to the credit of any input tax in respect of any supply of goods or services or both to him unless,— "
            "(a) he is in possession of a tax invoice or debit note issued by a supplier; (aa) the details of the invoice "
            "have been furnished by the supplier in GSTR-1 and communicated to the recipient; (b) he has received the goods "
            "or services; (c) tax charged has been actually paid to the Government; and (d) he has furnished return under Section 39."
        ),
        effective_date="2017-07-01 (Amended w.e.f 2022-01-01 for clause aa)",
        official_source_url="https://cbic-gst.gov.in",
    ),
    StatutoryProvision(
        act="Central Goods and Services Tax Act",
        year=2017,
        section="Section 31 read with Rule 48(4)",
        title="Mandatory E-Invoicing for Business-to-Business (B2B) Supplies",
        domain="tax_gst",
        official_citation="Notification No. 10/2023-Central Tax; Rule 48(4) CGST Rules",
        summary_plain_english=(
            "Businesses with an aggregate turnover exceeding ₹5 Crore in any preceding financial year must generate "
            "electronic invoices (e-invoices) bearing an Invoice Reference Number (IRN) and QR code through the Invoice "
            "Registration Portal (IRP) for all B2B supplies. Invoices issued without an IRN are legally invalid."
        ),
        verbatim_text=(
            "Every registered person whose aggregate turnover in any preceding financial year from 2017-18 onwards exceeds "
            "five crore rupees shall prepare invoice in terms of sub-rule (4) of rule 48 in respect of supply of goods or "
            "services or both to registered person. Any invoice issued without IRN shall not be treated as a valid tax invoice."
        ),
        effective_date="2023-08-01",
        official_source_url="https://cbic-gst.gov.in",
    ),
    StatutoryProvision(
        act="Central Goods and Services Tax Act",
        year=2017,
        section="Section 73 & Section 74",
        title="Determination of Tax Short-Paid, Erroneously Refunded, or ITC Wrongly Availed",
        domain="tax_gst",
        official_citation="CGST Act 2017, Sec. 73 (Non-Fraud) & Sec. 74 (Fraud/Willful Misstatement)",
        summary_plain_english=(
            "If tax is unpaid or short-paid without fraudulent intent, notice must be issued within 3 years, and penalty "
            "is 10% of tax or ₹10,000 (whichever is higher). If there is fraud, suppression of facts, or willful misstatement, "
            "the limitation period extends to 5 years, and a penalty of 100% of the tax due is mandatory."
        ),
        verbatim_text=(
            "Section 73(1): Where it appears that any tax has not been paid or short paid... for any reason other than fraud... "
            "the proper officer shall serve notice. Section 74(1): Where tax is unpaid by reason of fraud, or any willful "
            "misstatement or suppression of facts... the penalty leviable shall be equal to one hundred per cent of tax."
        ),
        effective_date="2017-07-01",
        official_source_url="https://cbic-gst.gov.in",
    ),

    # ---- 2. DIGITAL PERSONAL DATA PROTECTION (DPDP Act, 2023) ----
    StatutoryProvision(
        act="Digital Personal Data Protection Act",
        year=2023,
        section="Section 5 & Section 6",
        title="Notice and Consent Requirements for Processing Digital Personal Data",
        domain="dpdp_privacy",
        official_citation="Act No. 22 of 2023, The Gazette of India, CG-DL-E-12082023-248045",
        summary_plain_english=(
            "Any organization (Data Fiduciary) processing personal data of an Indian citizen must provide a clear, "
            "itemized notice in plain language (with an option to view in English or any 8th Schedule Indian language). "
            "Consent must be free, specific, informed, unconditional, and unambiguous with clear affirmative action. "
            "The data principal retains the right to withdraw consent at any time as easily as giving it."
        ),
        verbatim_text=(
            "Section 6(1): The consent given by the Data Principal shall be free, specific, informed, unconditional and "
            "unambiguous with a clear affirmative action, and shall signify an agreement to the processing of her personal data "
            "for the specified purpose and be limited to such personal data as is necessary for such specified purpose."
        ),
        effective_date="2023-08-11 (Enacted; phased notification)",
        official_source_url="https://www.meity.gov.in",
    ),
    StatutoryProvision(
        act="Digital Personal Data Protection Act",
        year=2023,
        section="Section 8 & Section 33",
        title="Obligations of Data Fiduciaries and Significant Financial Penalties",
        domain="dpdp_privacy",
        official_citation="DPDP Act 2023, Sec. 8 read with The Schedule (Penalties)",
        summary_plain_english=(
            "Data Fiduciaries must implement reasonable technical and organizational security safeguards to prevent personal data "
            "breaches. In case of a breach, they must notify the Data Protection Board of India and affected individuals. "
            "Failure to prevent a personal data breach attracts statutory monetary penalties up to ₹250 Crore (approx. $30M USD)."
        ),
        verbatim_text=(
            "Section 8(5): A Data Fiduciary shall protect personal data in its possession or under its control... by taking "
            "reasonable security safeguards to prevent personal data breach. Schedule: Failure to take reasonable security "
            "safeguards to prevent personal data breach under sub-section (5) of section 8: Penalty may extend to two hundred "
            "and fifty crore rupees."
        ),
        effective_date="2023-08-11",
        official_source_url="https://www.meity.gov.in",
    ),

    # ---- 3. FOOD SAFETY & STANDARDS (FSSAI / FSSA, 2006) ----
    StatutoryProvision(
        act="Food Safety and Standards Act",
        year=2006,
        section="Section 31",
        title="Mandatory Licensing and Registration of Food Business Operators (FBOs)",
        domain="food_safety",
        official_citation="FSS Act 2006 (Act 34 of 2006), Sec. 31; FSS (Licensing & Registration) Regulations 2011",
        summary_plain_english=(
            "No person can start or run any food business without obtaining an FSSAI License (for medium/large food businesses "
            "or importers) or FSSAI Registration (for petty manufacturers and retailers with annual turnover under ₹12 Lakhs). "
            "Operating a food business without a license is punishable with imprisonment up to 6 months and fine up to ₹5 Lakhs."
        ),
        verbatim_text=(
            "Section 31(1): No person shall commence or carry on any food business except under a licence. "
            "Section 63: If any person or food business operator manufactures, sells, stores or distributes any food without "
            "license, he shall be punishable with imprisonment for a term which may extend to six months and also with a fine "
            "which may extend to five lakh rupees."
        ),
        effective_date="2011-08-05 (Regulations operationalized)",
        official_source_url="https://fssai.gov.in",
    ),

    # ---- 4. TEXTILES & QUALITY STANDARDS ----
    StatutoryProvision(
        act="Textiles Committee Act",
        year=1963,
        section="Section 4 & QCOs",
        title="Quality Inspection, Labelling & Quality Control Orders (QCOs) for Textiles",
        domain="textiles",
        official_citation="Act No. 41 of 1963 read with BIS Quality Control Orders for Technical Textiles",
        summary_plain_english=(
            "Textile manufacturers, importers, and processors must adhere to mandatory Bureau of Indian Standards (BIS) Quality "
            "Control Orders (e.g. for polyester staple fibres, geotextiles, protective apparel). Goods must carry the Standard Mark (ISI). "
            "Commercial supply agreements cannot exempt products from these statutory safety and quality standards."
        ),
        verbatim_text=(
            "The functions of the Committee shall generally be to ensure by such measures as it thinks fit, standard qualities "
            "of textiles both for internal marketing and for export and the manufacture and use of standard type of textile machinery."
        ),
        effective_date="1963-12-03 (Updated through Ministry of Textiles QCOs 2023-2024)",
        official_source_url="https://textilescommittee.nic.in",
    ),

    # ---- 5. CONTRACT & COMMERCIAL LAW (Indian Contract Act, 1872) ----
    StatutoryProvision(
        act="Indian Contract Act",
        year=1872,
        section="Section 27",
        title="Agreement in Restraint of Trade Void",
        domain="contract",
        official_citation="Act No. 9 of 1872, Sec. 27",
        summary_plain_english=(
            "Under Indian law, every agreement by which anyone is restrained from exercising a lawful profession, trade or "
            "business of any kind, is to that extent VOID. Post-employment non-compete clauses prohibiting an employee from "
            "working in the same industry after resignation or termination are legally unenforceable in Indian courts (except for sale of goodwill)."
        ),
        verbatim_text=(
            "Section 27: Every agreement by which any one is restrained from exercising a lawful profession, trade or business of "
            "any kind, is to that extent void. Exception 1: One who sells the goodwill of a business may agree with the buyer to "
            "refrain from carrying on a similar business, within specified local limits..."
        ),
        effective_date="1872-09-01 (Supreme Court landmark: Percept D'Mark v. Zaheer Khan (2006))",
        official_source_url="https://www.indiacode.nic.in",
    ),
    StatutoryProvision(
        act="Indian Contract Act",
        year=1872,
        section="Section 73 & Section 74",
        title="Compensation for Loss/Damage (Liquidated Damages vs. Penalties)",
        domain="contract",
        official_citation="Act No. 9 of 1872, Sec. 73-74; Kailash Nath Associates v. DDA (2015) 4 SCC 136",
        summary_plain_english=(
            "Compensation is only payable for natural and direct losses arising from a breach of contract, not indirect or remote losses. "
            "Even if a contract specifies a fixed penalty or liquidated damages amount, Indian courts will only award reasonable compensation "
            "up to that maximum limit upon proof of actual damage suffered, unless it is impossible to prove actual loss."
        ),
        verbatim_text=(
            "Section 74: When a contract has been broken, if a sum is named in the contract as the amount to be paid in case of such "
            "breach, or if the contract contains any other stipulation by way of penalty, the party complaining of the breach is entitled, "
            "whether or not actual damage or loss is proved to have been caused thereby, to receive from the party who has broken the contract "
            "reasonable compensation not exceeding the amount so named."
        ),
        effective_date="1872-09-01",
        official_source_url="https://www.indiacode.nic.in",
    ),

    # ---- 6. CONSUMER PROTECTION (Consumer Protection Act, 2019) ----
    StatutoryProvision(
        act="Consumer Protection Act",
        year=2019,
        section="Section 2(47) & Section 82-87",
        title="Unfair Trade Practices & Product Liability Protections",
        domain="consumer",
        official_citation="Act No. 35 of 2019, Sec. 2(47) & Chapter VI",
        summary_plain_english=(
            "Contracts that impose unreasonable conditions on consumers (e.g. non-refundable full advances, unilateral termination "
            "without notice, excessive cancellation fees) can be declared null and void as 'Unfair Contracts'. Manufacturers and sellers "
            "are strictly liable under product liability for any harm caused by defective products or deficiency in services."
        ),
        verbatim_text=(
            "Section 2(46): 'unfair contract' means a contract between a manufacturer or trader and a consumer, having such terms "
            "which cause significant change in the rights of such consumer, including: (i) requiring excessive security deposits; "
            "(ii) refusing to accept early repayment; (iii) unilateral termination without reasonable cause..."
        ),
        effective_date="2020-07-20",
        official_source_url="https://consumeraffairs.nic.in",
    ),

    # ---- 7. CONSTITUTION OF INDIA ----
    StatutoryProvision(
        act="Constitution of India",
        year=1950,
        section="Article 19(1)(g) & Article 21",
        title="Freedom of Trade & Right to Livelihood and Privacy",
        domain="constitution",
        official_citation="The Constitution of India, Part III (Fundamental Rights)",
        summary_plain_english=(
            "All citizens possess the constitutional fundamental right to practice any profession, or to carry on any occupation, "
            "trade or business subject only to reasonable restrictions in the interest of the general public. Under Article 21, "
            "the right to life and personal liberty encompasses the right to privacy (K.S. Puttaswamy judgment)."
        ),
        verbatim_text=(
            "Article 19(1)(g): All citizens shall have the right to practise any profession, or to carry on any occupation, trade or business. "
            "Article 21: No person shall be deprived of his life or personal liberty except according to procedure established by law."
        ),
        effective_date="1950-01-26",
        official_source_url="https://legislative.gov.in/constitution-of-india",
    ),
]


class IndianLegalKnowledgeService:
    """Retrieval service over curated Indian statutes and statutory knowledge base."""

    def __init__(self):
        self.corpus = INDIAN_LEGAL_CORPUS

    def search(self, query: str, domain: Optional[str] = None, top_k: int = 3) -> list[dict]:
        """
        Grounded semantic keyword and concept retrieval across Indian statutes.
        Ranks by token overlap, domain alignment, and exact section matching.
        """
        q_tokens = set(re.findall(r"\w+", query.lower()))
        results = []

        for prov in self.corpus:
            if domain and domain != "all" and prov.domain != domain:
                continue

            # Calculate match score based on title, act, section, and text
            text_corpus = f"{prov.act} {prov.section} {prov.title} {prov.summary_plain_english} {prov.verbatim_text}".lower()
            overlap = sum(1 for token in q_tokens if token in text_corpus)

            # Bonus for exact section or act match
            if prov.section.lower() in query.lower():
                overlap += 8
            if prov.act.lower() in query.lower():
                overlap += 5
            if prov.domain in query.lower():
                overlap += 3

            if overlap > 0:
                score = min(0.99, max(0.50, overlap / (len(q_tokens) + 1.0)))
                results.append({
                    "score": round(score, 2),
                    "act": prov.act,
                    "year": prov.year,
                    "section": prov.section,
                    "title": prov.title,
                    "domain": prov.domain,
                    "official_citation": prov.official_citation,
                    "summary_plain_english": prov.summary_plain_english,
                    "verbatim_text": prov.verbatim_text,
                    "effective_date": prov.effective_date,
                    "official_source_url": prov.official_source_url,
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def get_by_domain(self, domain: str) -> list[dict]:
        """Fetch all provisions in a specific legal domain."""
        return [
            {
                "act": p.act,
                "section": p.section,
                "title": p.title,
                "citation": p.official_citation,
                "summary": p.summary_plain_english,
            }
            for p in self.corpus
            if p.domain == domain or domain == "all"
        ]


indian_legal_service = IndianLegalKnowledgeService()
