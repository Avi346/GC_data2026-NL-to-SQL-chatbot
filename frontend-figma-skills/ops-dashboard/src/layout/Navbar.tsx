import React from 'react';

interface NavbarProps {
  appMode: 'admin' | 'user';
  onModeChange: (mode: 'admin' | 'user') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ appMode, onModeChange }) => {
  return (
    <header
      className="h-20 flex items-center justify-between px-8 border-b border-white/5 relative z-10 w-full shrink-0"
      style={{
        background: 'rgba(255,255,255,0.01)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)'
      }}
    >
      {/* Search Input */}
      <div className="flex items-center gap-6 flex-1 min-w-0">
        <h2 className="text-xl font-bold text-[#ff4756] tracking-tighter shrink-0 hidden md:block" style={{ fontFamily: "'montreal-serial-extrabold', sans-serif", textShadow: '0 0 20px rgba(255, 71, 86, 0.2)' }}>

        </h2>
        <div className="relative w-full max-w-md group">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <svg className="h-4 w-4 text-gray-400 group-focus-within:text-[#ff4756] transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            placeholder="Search global channels, assets, insights..."
            className="block w-full pl-11 pr-14 py-2.5 min-h-[44px] border border-white/10 rounded-xl bg-black/40 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-[#ff4756]/50 focus:border-[#ff4756]/50 transition-all font-mono text-ellipsis overflow-hidden whitespace-nowrap"
          />
          <div className="absolute inset-y-0 right-0 pr-2 flex items-center">
            <kbd className="inline-flex items-center px-2 py-0.5 rounded border border-white/10 bg-white/5 text-[10px] font-mono font-medium text-gray-400 uppercase">
              Ctrl K
            </kbd>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4 relative z-10 mt-1">
        {/* Admin / User Mode Toggle */}
        <div className="flex items-center gap-1.5 p-1 rounded-full bg-white/[0.04] border border-white/10">
          <button
            onClick={() => onModeChange('admin')}
            className={`px-3.5 py-1.5 rounded-full text-[10px] font-semibold uppercase tracking-wider transition-all ${
              appMode === 'admin'
                ? 'bg-[#ff4756]/20 text-[#ff4756] border border-[#ff4756]/30 shadow-[0_0_10px_rgba(255,71,86,0.15)]'
                : 'text-gray-400 hover:text-gray-200 border border-transparent'
            }`}
          >
            Admin
          </button>
          <button
            onClick={() => onModeChange('user')}
            className={`px-3.5 py-1.5 rounded-full text-[10px] font-semibold uppercase tracking-wider transition-all ${
              appMode === 'user'
                ? 'bg-[#ff4756]/20 text-[#ff4756] border border-[#ff4756]/30 shadow-[0_0_10px_rgba(255,71,86,0.15)]'
                : 'text-gray-400 hover:text-gray-200 border border-transparent'
            }`}
          >
            User
          </button>
        </div>

        {/* Environment Badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#ff4756]/10 border border-[#ff4756]/20 shrink-0">
          <span className="w-2 h-2 rounded-full bg-[#ff4756] shadow-[0_0_8px_#ff4756] animate-pulse" />
          <span className="text-[10px] uppercase font-mono tracking-wider font-semibold text-[#ff4756]">Production</span>
        </div>

        {/* Date Display */}
        <div className="text-right hidden sm:block shrink-0 min-w-max pr-4">
          <p className="text-xs text-gray-400 font-mono tracking-wide break-none whitespace-nowrap">MAR 17, 2026</p>
          <p className="text-[10px] text-gray-600 uppercase tracking-widest leading-tight whitespace-nowrap mt-0.5">Last sync 2m ago</p>
        </div>

        {/* Separator */}
        <div className="w-px h-8 bg-white/10 shrink-0" />

        {/* Action Icons */}
        <div className="flex items-center gap-2 shrink-0 pr-4">
          <button className="w-10 h-10 min-w-[40px] rounded-full hover:bg-white/10 flex items-center justify-center text-gray-400 hover:text-white transition-colors relative">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span className="absolute top-2 right-2.5 w-2 h-2 rounded-full bg-rose-500 shadow-[0_0_8px_#f43f5e]" />
          </button>
        </div>
      </div>
    </header>
  );
};
