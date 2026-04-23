import React, { useState } from 'react';
import { GlassCard } from './GlassCard';

interface Column<T> {
  header: string;
  accessor: keyof T;
  render?: (value: any, row: T) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  searchPlaceholder?: string;
  itemsPerPage?: number;
}

export function DataTable<T>({ 
  columns, 
  data, 
  searchPlaceholder = "Search...", 
  itemsPerPage = 10 
}: DataTableProps<T>) {
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);

  // Simple hardcoded field search for mock purposes
  const filteredData = data.filter(item => 
    Object.values(item as any).some(val => 
      String(val).toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const paginatedData = filteredData.slice((page - 1) * itemsPerPage, page * itemsPerPage);

  return (
    <GlassCard padding="none" className="flex flex-col h-full">
      {/* Search and Filters Bar - Breathing room with px-6 py-4 */}
      <div className="flex items-center justify-between px-6 py-5 border-b border-white/[0.04]">
        <div className="relative w-72">
          <svg className="w-4 h-4 text-[#ff4756]/50 absolute left-3 top-1/2 -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input 
            type="text" 
            placeholder={searchPlaceholder}
            className="w-full bg-black/40 border border-white/5 rounded-full pl-10 pr-4 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-[#ff4756]/50 focus:ring-1 focus:ring-[#ff4756]/50 transition-all font-mono"
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}
          />
        </div>
        
        <div className="flex gap-3">
          {/* Mock Filter Buttons */}
          <button className="px-4 py-2 rounded-full border border-white/10 text-xs text-gray-400 hover:text-white hover:bg-white/5 transition-colors flex items-center gap-2">
            Status
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
          </button>
          <button className="px-4 py-2 rounded-full border border-white/10 text-xs text-gray-400 hover:text-white hover:bg-white/5 transition-colors flex items-center gap-2">
            Platform
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
          </button>
        </div>
      </div>

      {/* Table Area */}
      <div className="flex-1 overflow-auto">
        <table className="w-full text-left border-collapse min-w-[800px]">
          <thead>
            <tr className="border-b border-white/[0.04] bg-white/[0.01]">
              {columns.map((col, i) => (
                <th 
                  key={i}
                  className="px-6 py-4 text-left text-[10px] uppercase font-bold text-gray-500 tracking-widest bg-black/40 backdrop-blur-md sticky top-0 z-20 border-b border-white/5"
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.02]">
            {paginatedData.map((row, i) => (
              <tr key={i} className="hover:bg-white/[0.02] transition-colors group cursor-default">
                {columns.map((col, j) => (
                  <td 
                    key={j} 
                    className="px-6 py-4 whitespace-nowrap text-[13px] font-medium text-gray-400 group-hover:text-gray-200 transition-colors"
                  >
                    {col.render ? col.render(row[col.accessor], row) : String(row[col.accessor])}
                  </td>
                ))}
              </tr>
            ))}
            {paginatedData.length === 0 && (
              <tr>
                <td colSpan={columns.length} className="px-6 py-12 text-center text-gray-500 text-sm">
                  No results found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      <div className="flex items-center justify-between px-6 py-4 border-t border-white/[0.04]">
        <span className="text-xs text-gray-600 font-mono">
          Showing {Math.min((page - 1) * itemsPerPage + 1, filteredData.length)} to {Math.min(page * itemsPerPage, filteredData.length)} of {filteredData.length} entries
        </span>
        
        <div className="flex gap-2">
          <button 
            disabled={page === 1}
            onClick={() => setPage(p => p - 1)}
            className="w-8 h-8 rounded-lg flex items-center justify-center border border-white/10 text-gray-400 hover:text-white hover:bg-white/5 disabled:opacity-30 disabled:hover:bg-transparent transition-colors"
          >
            ←
          </button>
          <div className="px-4 flex items-center justify-center text-xs text-[#ff4756] font-mono">
            {page} / {totalPages || 1}
          </div>
          <button 
            disabled={page === totalPages || totalPages === 0}
            onClick={() => setPage(p => p + 1)}
            className="w-8 h-8 rounded-lg flex items-center justify-center border border-white/10 text-gray-400 hover:text-white hover:bg-white/5 disabled:opacity-30 disabled:hover:bg-transparent transition-colors"
          >
            →
          </button>
        </div>
      </div>
    </GlassCard>
  );
}
