import React, { useState, useRef } from 'react';
import { Upload, FileUp, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { useDashboardData } from '../context/DashboardContext';

export const DataIngestion: React.FC = () => {
  const { refreshData } = useDashboardData();
  const [file, setFile] = useState<File | null>(null);
  const [dataType, setDataType] = useState<string>('userData');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage({ type: 'error', text: 'Please select a file first.' });
      return;
    }

    setUploading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('dataType', dataType);

    try {
      const response = await fetch('http://localhost:5000/api/upload-csv', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Upload failed');
      }

      setMessage({ type: 'success', text: result.message || 'File uploaded successfully!' });
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      
      refreshData();

    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'An unexpected error occurred.' });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">Data Ingestion</h1>
        <p className="text-gray-400">Upload CSV exports here. The data will be parsed, securely upserted into the PostgreSQL database, and the dashboard will instantly refresh.</p>
      </div>

      <div className="card p-6 border-brand-red/20 mb-6 bg-[#13181e] rounded-xl">
        <h2 className="text-lg font-semibold mb-4 text-white">Upload New Data</h2>

        <div className="mb-6">
          <label className="block text-brand-red font-medium mb-2 text-sm tracking-widest uppercase">Target Data Table</label>
          <select 
            value={dataType}
            onChange={(e) => setDataType(e.target.value)}
            className="w-full bg-[#0a0f12] border border-brand-red/30 rounded-lg p-3 text-white focus:outline-none focus:border-brand-red"
          >
            <option value="userData">User Analytics</option>
          </select>
        </div>

        <div 
          className={`border-2 border-dashed rounded-xl p-10 text-center transition-colors cursor-pointer ${file ? 'border-brand-green/50 bg-brand-green/5' : 'border-gray-700 bg-[#0a0f12] hover:border-brand-red/50 hover:bg-brand-red/5'}`}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="flex flex-col items-center justify-center space-y-4">
            {file ? (
              <>
                <FileUp size={48} className="text-brand-green" />
                <div>
                  <p className="text-lg font-medium text-brand-green font-mono">{file.name}</p>
                  <p className="text-sm text-gray-500 mt-1">Ready to upload ({(file.size / 1024).toFixed(1)} KB)</p>
                </div>
              </>
            ) : (
              <>
                <div className="p-4 bg-brand-red/10 rounded-full">
                  <Upload size={32} className="text-brand-red" />
                </div>
                <div>
                  <p className="text-lg font-medium text-white">Click or drag CSV file to this area</p>
                  <p className="text-sm text-gray-500 mt-1">Supports standard CSV formatting</p>
                </div>
              </>
            )}
          </div>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            accept=".csv" 
            className="hidden" 
          />
        </div>

        {message && (
          <div className={`mt-6 p-4 rounded-lg flex items-start space-x-3 ${message.type === 'success' ? 'bg-brand-green/10 border border-brand-green/20' : 'bg-red-500/10 border border-red-500/20'}`}>
            {message.type === 'success' ? (
              <CheckCircle2 className="text-brand-green shrink-0 mt-0.5" size={20} />
            ) : (
              <AlertCircle className="text-red-500 shrink-0 mt-0.5" size={20} />
            )}
            <div>
              <p className={`font-medium ${message.type === 'success' ? 'text-brand-green' : 'text-red-500'}`}>
                {message.type === 'success' ? 'Success' : 'Upload Failed'}
              </p>
              <p className={`text-sm mt-1 ${message.type === 'success' ? 'text-brand-green/80' : 'text-red-500/80'}`}>
                {message.text}
              </p>
            </div>
          </div>
        )}

        <div className="mt-8 flex justify-end">
          <button
            disabled={!file || uploading}
            onClick={(e) => { e.stopPropagation(); handleUpload(); }}
            className="flex items-center space-x-2 bg-brand-red hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-colors focus:ring-4 focus:ring-brand-red/20 outline-none"
          >
            {uploading ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Upload size={20} />
                <span>Upload & Upsert Data</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
