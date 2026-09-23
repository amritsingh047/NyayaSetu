'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Loader2, X, Landmark, ShieldCheck } from 'lucide-react';
import { uploadDocument } from '@/lib/api';
import { useDocumentStore } from '@/store/document-store';

const INDIAN_JURISDICTIONS = [
  { value: 'india_central', label: 'All India (Central Law / Supreme Court)' },
  { value: 'maharashtra', label: 'Maharashtra (Bombay HC Jurisdiction)' },
  { value: 'delhi', label: 'NCT of Delhi (Delhi HC Jurisdiction)' },
  { value: 'karnataka', label: 'Karnataka (Bengaluru Tech Corridor)' },
  { value: 'tamil_nadu', label: 'Tamil Nadu (Madras HC Jurisdiction)' },
  { value: 'gujarat', label: 'Gujarat (Commercial & Industrial)' },
  { value: 'telangana', label: 'Telangana & Andhra Pradesh' },
  { value: 'west_bengal', label: 'West Bengal (Calcutta HC Jurisdiction)' },
];

const INDIAN_DOC_TYPES = [
  { value: 'generic', label: 'Auto-Detect Contract Type' },
  { value: 'commercial_supply', label: 'B2B Vendor / Commercial Supply (GST Compliant)' },
  { value: 'employment', label: 'Employment / Consultancy / Service Agreement' },
  { value: 'lease_rental', label: 'Commercial / Residential Lease (Rent Agreement)' },
  { value: 'nda_confidentiality', label: 'Non-Disclosure Agreement (NDA)' },
  { value: 'dpdp_privacy', label: 'Data Processing Addendum (DPDP Act 2023)' },
  { value: 'fssai_food', label: 'Food Supply / FSSAI Compliance Agreement' },
  { value: 'textiles_procurement', label: 'Textiles & Garment Supply Contract' },
];

interface Props {
  compact?: boolean;
}

export function DocumentUploader({ compact = false }: Props) {
  const [title, setTitle] = useState('');
  const [docType, setDocType] = useState('generic');
  const [jurisdiction, setJurisdiction] = useState('india_central');
  const [textContent, setTextContent] = useState('');
  const [activeInput, setActiveInput] = useState<'file' | 'text'>('file');
  const [status, setStatus] = useState<'idle' | 'uploading' | 'processing' | 'done' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);

  const { processingMode, setCurrentDocument, addDocument } = useDocumentStore();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;
    if (!title) setTitle(file.name.replace(/\.[^.]+$/, ''));
    await handleUpload(file);
  }, [title, processingMode]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'text/plain': ['.txt'], 'application/msword': ['.doc', '.docx'] },
    maxFiles: 1,
    disabled: status === 'uploading' || status === 'processing',
  });

  async function handleUpload(file?: File) {
    setStatus('uploading');
    setError(null);

    const formData = new FormData();
    formData.append('title', title || 'Indian Legal Agreement');
    formData.append('doc_type', docType);
    formData.append('jurisdiction', jurisdiction);
    formData.append('processing_mode', processingMode);

    if (file) {
      formData.append('file', file);
    } else if (textContent) {
      formData.append('text_content', textContent);
    } else {
      setError('Please select a PDF document or paste contract text.');
      setStatus('idle');
      return;
    }

    try {
      setStatus('processing');
      const doc = await uploadDocument(formData);
      addDocument(doc);
      setCurrentDocument(doc);
      setStatus('done');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Upload failed. Please check file format and try again.';
      setError(message);
      setStatus('error');
    }
  }

  if (compact) {
    return (
      <div className="bg-card border border-border rounded-xl p-4 shadow-sm">
        <h3 className="font-semibold text-xs uppercase tracking-wider text-muted-foreground mb-2">Document Actions</h3>
        <button
          onClick={() => useDocumentStore.getState().setCurrentDocument(null)}
          className="w-full text-xs font-medium border border-dashed border-border rounded-lg py-2.5 text-muted-foreground hover:border-primary hover:text-primary transition-colors flex items-center justify-center gap-1.5"
        >
          <span>+ Upload another document</span>
        </button>
      </div>
    );
  }

  return (
    <div className="bg-card border border-border rounded-2xl shadow-sm p-6 space-y-4">
      {/* Title */}
      <div>
        <label className="block text-xs font-bold text-foreground uppercase tracking-wider mb-1.5">
          Agreement or Document Title
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Master Supply Agreement (GST & FSSAI Compliant)"
          className="w-full border border-input rounded-xl px-3.5 py-2 text-xs bg-background focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>

      {/* Doc type + Jurisdiction */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-bold text-foreground uppercase tracking-wider mb-1.5">
            Agreement Category
          </label>
          <select
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
            className="w-full border border-input rounded-xl px-3 py-2 text-xs bg-background focus:outline-none focus:ring-2 focus:ring-ring"
          >
            {INDIAN_DOC_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs font-bold text-foreground uppercase tracking-wider mb-1.5">
            <Landmark className="h-3 w-3 inline mr-1 text-primary" /> Indian Jurisdiction / State
          </label>
          <select
            value={jurisdiction}
            onChange={(e) => setJurisdiction(e.target.value)}
            className="w-full border border-input rounded-xl px-3 py-2 text-xs bg-background focus:outline-none focus:ring-2 focus:ring-ring"
          >
            {INDIAN_JURISDICTIONS.map((j) => <option key={j.value} value={j.value}>{j.label}</option>)}
          </select>
        </div>
      </div>

      {/* File / Text Toggle */}
      <div className="flex rounded-xl border border-border overflow-hidden p-0.5 bg-muted/30">
        <button
          onClick={() => setActiveInput('file')}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
            activeInput === 'file' ? 'bg-primary text-primary-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          Upload PDF / Word
        </button>
        <button
          onClick={() => setActiveInput('text')}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
            activeInput === 'text' ? 'bg-primary text-primary-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          Paste Contract Text
        </button>
      </div>

      {/* File Drop Area */}
      {activeInput === 'file' && (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
            isDragActive
              ? 'border-primary bg-primary/5 scale-[0.99]'
              : 'border-border hover:border-primary/50 hover:bg-muted/40'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="h-9 w-9 text-primary/70 mx-auto mb-2" />
          <p className="text-xs font-bold text-foreground">
            {isDragActive ? 'Drop your agreement here' : 'Drag & drop contract PDF / DOCX or click to browse'}
          </p>
          <p className="text-[11px] text-muted-foreground mt-1">
            Max 25MB · Zero-retention transient processing · Aadhaar/PAN redacted automatically
          </p>
        </div>
      )}

      {/* Direct Text Paste */}
      {activeInput === 'text' && (
        <textarea
          value={textContent}
          onChange={(e) => setTextContent(e.target.value)}
          placeholder="Paste contract clauses, policy provisions, or GST dispute notices here..."
          rows={7}
          className="w-full border border-input rounded-xl px-3.5 py-2.5 text-xs bg-background focus:outline-none focus:ring-2 focus:ring-ring resize-none font-mono"
        />
      )}

      {/* Error message */}
      {error && (
        <div className="flex items-center gap-2 text-destructive text-xs bg-destructive/10 rounded-lg px-3 py-2">
          <X className="h-4 w-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Submit Button */}
      <button
        onClick={() => handleUpload()}
        disabled={status === 'uploading' || status === 'processing'}
        className="w-full bg-primary text-primary-foreground rounded-xl py-3 font-semibold text-xs hover:opacity-90 disabled:opacity-50 transition-all flex items-center justify-center gap-2 shadow-sm"
      >
        {(status === 'uploading' || status === 'processing') ? (
          <><Loader2 className="h-4 w-4 animate-spin" /> Analyzing Agreement under Indian Law...</>
        ) : (
          <><FileText className="h-4 w-4" /> Analyze Document</>
        )}
      </button>

      {/* Privacy Guarantee & Mode Switch */}
      <div className="flex items-center justify-between text-[11px] text-muted-foreground pt-1 border-t border-border/50">
        <div className="flex items-center gap-1.5">
          <ShieldCheck className="h-3.5 w-3.5 text-green-600" />
          <span>DPDP Act 2023 Compliant: Zero Data Retention</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => useDocumentStore.getState().setProcessingMode('cloud')}
            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
              processingMode === 'cloud' ? 'bg-primary text-primary-foreground' : 'bg-muted'
            }`}
          >
            Cloud
          </button>
          <button
            onClick={() => useDocumentStore.getState().setProcessingMode('local')}
            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
              processingMode === 'local' ? 'bg-primary text-primary-foreground' : 'bg-muted'
            }`}
          >
            Local (Offline)
          </button>
        </div>
      </div>
    </div>
  );
}
