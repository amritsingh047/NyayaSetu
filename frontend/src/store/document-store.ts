import { create } from 'zustand';

export interface DocumentRecord {
  id: string;
  title: string;
  file_name: string;
  doc_type: string;
  jurisdiction: string;
  status: string;
  page_count?: number;
  word_count?: number;
  processing_mode: string;
  uploaded_at: string;
}

interface DocumentStore {
  currentDocument: DocumentRecord | null;
  documents: DocumentRecord[];
  disclaimerAccepted: boolean;
  processingMode: 'cloud' | 'local';
  setCurrentDocument: (doc: DocumentRecord | null) => void;
  addDocument: (doc: DocumentRecord) => void;
  acceptDisclaimer: () => void;
  setProcessingMode: (mode: 'cloud' | 'local') => void;
}

export const useDocumentStore = create<DocumentStore>((set) => ({
  currentDocument: null,
  documents: [],
  disclaimerAccepted: false,
  processingMode: 'cloud',

  setCurrentDocument: (doc) => set({ currentDocument: doc }),
  addDocument: (doc) => set((state) => ({ documents: [...state.documents, doc] })),
  acceptDisclaimer: () => set({ disclaimerAccepted: true }),
  setProcessingMode: (mode) => set({ processingMode: mode }),
}));
