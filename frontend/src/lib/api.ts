/**
 * LexAI API client using axios.
 * All endpoints route through the FastAPI backend.
 */
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
});

// Attach Firebase token if present
apiClient.interceptors.request.use(async (config) => {
  try {
    const { auth } = await import('@/lib/firebase');
    const user = auth.currentUser;
    if (user) {
      const token = await user.getIdToken();
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch {
    // No auth token available (anonymous session)
  }
  return config;
});

// ---- Document APIs ----

export async function uploadDocument(formData: FormData) {
  const res = await apiClient.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function deleteDocument(documentId: string) {
  await apiClient.delete(`/documents/${documentId}`);
}

// ---- Analysis APIs ----

export async function generateSummary(documentId: string, readingLevel: string = 'standard') {
  const res = await apiClient.post('/analysis/summary', { document_id: documentId, reading_level: readingLevel });
  return res.data;
}

export async function askQuestion(documentId: string, question: string) {
  const res = await apiClient.post('/analysis/qa', { document_id: documentId, question });
  return res.data;
}

export async function generateChecklist(documentId: string) {
  const res = await apiClient.post('/analysis/checklist', { document_id: documentId });
  return res.data;
}

export async function getClauses(documentId: string) {
  const res = await apiClient.get(`/analysis/clauses/${documentId}`);
  return res.data;
}

export async function compareDocuments(docAId: string, docBId: string) {
  const res = await apiClient.post('/analysis/compare', { doc_a_id: docAId, doc_b_id: docBId });
  return res.data;
}
