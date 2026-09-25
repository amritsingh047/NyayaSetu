"""
Comprehensive test suite for NyayaSetu — AI-Assisted Legal Information Platform (India).
Tests:
1. Indian PII Redaction (DPDP Act compliance: Aadhaar, PAN, Mobile, GSTIN, IFSC).
2. Safety Guardrails & Advice-Seeking Refusal with Advocate / NALSA escalation.
3. Statutory RAG grounding across Indian legal corpus.
4. Clause risk analysis under Indian statutory law (Sec 27 Restraint of Trade, Sec 74 Penalty).
5. Document comparison and conflict detection.
6. Actionable checklist & 'Tasks before consulting an Advocate' generation.
"""
import unittest
import asyncio
from app.services.document_processor import DocumentProcessor
from app.services.guardrails import GuardrailsService
from app.services.indian_legal_corpus import IndianLegalKnowledgeService
from app.services.llm_orchestrator import LLMOrchestrator


class TestIndianLegalPlatform(unittest.TestCase):
    def setUp(self):
        self.processor = DocumentProcessor()
        self.guardrails = GuardrailsService()
        self.corpus = IndianLegalKnowledgeService()
        self.orchestrator = LLMOrchestrator()

    # ---- 1. PII Redaction (DPDP Act Compliance) ----
    def test_aadhaar_redaction(self):
        sample = "The party identity proof is Aadhaar 5432 1098 7654 attached herewith."
        redacted = self.processor.strip_pii(sample)
        self.assertNotIn("5432 1098 7654", redacted)
        self.assertIn("[AADHAAR-REDACTED]", redacted)

    def test_pan_redaction(self):
        sample = "Vendor Tax ID PAN is ABCDE1234F for GST verification."
        redacted = self.processor.strip_pii(sample)
        self.assertNotIn("ABCDE1234F", redacted)
        self.assertIn("[PAN-REDACTED]", redacted)

    def test_indian_mobile_redaction(self):
        sample = "Contact the authorized representative at +91 9876543210 or 9123456780."
        redacted = self.processor.strip_pii(sample)
        self.assertNotIn("9876543210", redacted)
        self.assertNotIn("9123456780", redacted)
        self.assertIn("[MOBILE-REDACTED]", redacted)

    def test_gstin_and_ifsc_redaction(self):
        sample = "Supplier GSTIN is 27ABCDE1234F1Z5 and bank branch IFSC is HDFC0001234."
        redacted = self.processor.strip_pii(sample)
        self.assertNotIn("27ABCDE1234F1Z5", redacted)
        self.assertNotIn("HDFC0001234", redacted)
        self.assertIn("[GSTIN-REDACTED]", redacted)
        self.assertIn("[IFSC-REDACTED]", redacted)

    # ---- 2. Advice Refusal & Advocate Escalation ----
    def test_advice_seeking_queries_refused(self):
        prohibited_queries = [
            "Should I sue my supplier for delay in delivery?",
            "Can I sue the landlord in consumer court?",
            "Will I win this case if I file a petition?",
            "What strategy should my lawyer take?",
            "Should I file an FIR against the contractor?",
            "Give me legal advice on how to breach this agreement",
        ]
        for query in prohibited_queries:
            with self.subTest(query=query):
                self.assertTrue(
                    self.guardrails.is_advice_seeking(query),
                    f"Failed to detect advice-seeking query: {query}",
                )

    def test_legitimate_information_queries_allowed(self):
        permitted_queries = [
            "What is the termination notice period specified in clause 12?",
            "What are the GST invoice eligibility rules under Section 16?",
            "Explain the difference between liquidated damages and penalty under Indian law",
            "What is a Vakalatnama and who can sign it?",
        ]
        for query in permitted_queries:
            with self.subTest(query=query):
                self.assertFalse(
                    self.guardrails.is_advice_seeking(query),
                    f"Falsely blocked legitimate informational query: {query}",
                )

    def test_advocate_escalation_payload(self):
        refusal = self.guardrails.build_advice_refusal()
        self.assertTrue(refusal["is_out_of_scope"])
        self.assertIn("escalation", refusal)
        self.assertEqual(refusal["escalation"]["free_legal_aid"]["authority"], "National Legal Services Authority (NALSA)")
        self.assertIn("15100", refusal["escalation"]["free_legal_aid"]["helpline"])

    # ---- 3. Statutory RAG Grounding ----
    def test_statutory_corpus_gst_itc_retrieval(self):
        results = self.corpus.search("Input tax credit conditions GSTR 2B supplier", domain="tax_gst")
        self.assertGreater(len(results), 0)
        top = results[0]
        self.assertEqual(top["act"], "Central Goods and Services Tax Act")
        self.assertEqual(top["section"], "Section 16")
        self.assertIn("GSTR-1", top["verbatim_text"])

    def test_statutory_corpus_restraint_of_trade(self):
        results = self.corpus.search("non compete employment restraint of trade", domain="contract")
        self.assertGreater(len(results), 0)
        top = results[0]
        self.assertEqual(top["section"], "Section 27")
        self.assertIn("void", top["summary_plain_english"].lower())

    def test_statutory_corpus_dpdp_penalties(self):
        results = self.corpus.search("digital personal data protection breach penalty", domain="dpdp_privacy")
        self.assertGreater(len(results), 0)
        top = results[0]
        self.assertIn("250", top["summary_plain_english"])

    # ---- 4. Clause Risk Analysis ----
    def test_clause_risk_restraint_of_trade(self):
        clause = "Employee shall not engage in any similar business or employment for 2 years following termination."
        analysis = self.orchestrator._analyze_clause_statutory(clause, "employment", "")
        self.assertEqual(analysis["risk_level"], "HIGH")
        self.assertIn("Section 27", analysis["risk_justification"])

    def test_clause_risk_unlimited_indemnity(self):
        clause = "Supplier agrees to indemnify, defend, and hold harmless Purchaser from all claims, losses, and damages."
        analysis = self.orchestrator._analyze_clause_statutory(clause, "commercial_supply", "")
        self.assertEqual(analysis["risk_level"], "HIGH")
        self.assertIn("liability cap", analysis["options"][0].lower())

    # ---- 5. Document Comparison & Conflict Detection ----
    def test_document_comparison_notice_divergence(self):
        doc_a = "Either party may terminate by giving 30 days written notice."
        doc_b = "Either party may terminate by giving 90 days written notice."
        comp = self.orchestrator._compare_contracts_grounded(doc_a, doc_b, "Version 1", "Version 2")
        self.assertGreater(len(comp["differences"]), 0)
        notice_diff = next((d for d in comp["differences"] if "Notice" in d["section"]), None)
        self.assertIsNotNone(notice_diff)
        self.assertIn("30", notice_diff["summary"])
        self.assertIn("90", notice_diff["summary"])

    # ---- 6. Actionable Checklist & Advocate Preparation ----
    def test_tasks_before_consulting_advocate_present(self):
        sample_doc = "Contract dated 15th August 2024 with 30 days notice period and GST compliance."
        checklist = self.orchestrator._extract_action_items_and_checklist(sample_doc, "Buyer")
        self.assertIn("red_flags", checklist)
        self.assertIn("required_actions", checklist)
        # Verify pre-advocate dossier item is present
        advocate_items = [item for item in checklist["red_flags"] if "Advocate" in item["item"]]
        self.assertGreater(len(advocate_items), 0)
        self.assertIn("payment transaction proofs", advocate_items[0]["item"])


if __name__ == "__main__":
    unittest.main()
