import React from 'react';
import { useDashboardData } from '../context/DashboardContext';
import { DataTable } from '../components/DataTable';
import type { UserData } from '../types';

export const VideoExplorer: React.FC = () => {
  const { userData } = useDashboardData();

  const columns = [
    {
      header: 'User',
      accessor: 'name' as keyof UserData,
      render: (val: string, row: UserData) => (
        <div className="flex items-center gap-3 min-w-[180px]">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#ff4756]/20 to-[#ffb7bc]/20 border border-white/5 flex items-center justify-center shrink-0">
            <span className="text-[10px] font-bold text-[#ffb7bc]">
              {val.split(' ').map(n => n[0]).join('').slice(0, 2)}
            </span>
          </div>
          <div className="flex flex-col gap-0.5">
            <span className="text-[14px] font-bold text-white tracking-tight group-hover:text-[#ff4756] transition-colors leading-none">{val}</span>
            <span className="text-[10px] text-gray-500 font-mono">{row.published > 0 ? 'Publisher' : 'Ghost User'}</span>
          </div>
        </div>
      )
    },
    {
      header: 'Uploaded',
      accessor: 'uploaded' as keyof UserData,
      render: (val: number) => (
        <span className="text-sm font-semibold text-gray-200">{val.toLocaleString()}</span>
      )
    },
    {
      header: 'AI Created',
      accessor: 'created' as keyof UserData,
      render: (val: number) => (
        <span className="text-sm font-semibold text-gray-300">{val.toLocaleString()}</span>
      )
    },
    {
      header: 'Published',
      accessor: 'published' as keyof UserData,
      render: (val: number) => (
        <span className={`text-sm font-bold ${val > 0 ? 'text-emerald-400' : 'text-gray-600'}`}>
          {val > 0 ? val.toLocaleString() : '—'}
        </span>
      )
    },
    {
      header: 'Publish Rate',
      accessor: 'publishRate' as keyof UserData,
      render: (val: number) => {
        const color = val >= 1.5 ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' :
          val > 0 ? 'text-amber-400 bg-amber-500/10 border-amber-500/20' :
            'text-gray-500 bg-gray-500/10 border-gray-500/20';
        return (
          <span className={`px-2.5 py-1 rounded-md border text-[11px] font-mono font-semibold ${color}`}>
            {val > 0 ? `${val}%` : '0%'}
          </span>
        );
      }
    },
    {
      header: 'Upload Duration',
      accessor: 'uploadedDuration' as keyof UserData,
      render: (val: string) => (
        <span className="font-mono text-gray-400 text-sm">{val}</span>
      )
    },
    {
      header: 'Created Duration',
      accessor: 'createdDuration' as keyof UserData,
      render: (val: string) => (
        <span className="font-mono text-gray-400 text-sm">{val}</span>
      )
    },
  ];

  return (
    <div className="h-[calc(100vh-180px)] min-h-[500px] pb-8 page-enter flex flex-col">
      <DataTable
        data={userData}
        columns={columns}
        searchPlaceholder="Find user by name..."
        itemsPerPage={12}
      />
    </div>
  );
};
