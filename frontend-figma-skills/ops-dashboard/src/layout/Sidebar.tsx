import React from 'react';

export interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
}

interface SidebarProps {
  items: NavItem[];
  activeId: string;
  onNavigate: (id: string) => void;
  isOpen: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ items, activeId, onNavigate, isOpen, onToggle }) => {
  return (
    <aside
      className={`flex-shrink-0 h-full flex flex-col relative z-20 border-r border-white/5 transition-all duration-300 ease-in-out ${isOpen ? 'w-64' : 'w-[88px]'}`}
      style={{
        background: 'rgba(255,255,255,0.01)',
        backdropFilter: 'blur(40px)',
        WebkitBackdropFilter: 'blur(40px)'
      }}
    >
      {/* Brand Header */}
      <div className={`h-20 flex items-center border-b border-white/5 relative overflow-hidden transition-all duration-300 ${isOpen ? 'px-8' : 'justify-center px-0'}`}>
        {/* Subtle glow accent */}
        <div className="absolute -top-10 -left-10 w-32 h-32 bg-[#ff4756]/10 rounded-full blur-2xl pointer-events-none" />

        <div className={`flex items-center relative z-10 w-full mt-2 transition-all ${isOpen ? 'gap-3' : 'justify-center gap-0'}`}>
          {/* Hamburger Toggle / Logo Replacement */}
          <button
            onClick={onToggle}
            className="w-10 h-10 rounded-lg flex items-center justify-center hover:bg-white/10 text-gray-400 hover:text-white transition-colors shrink-0"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          {/* Typographic Lockup */}
          <div className={`flex items-center transition-all duration-300 overflow-hidden ${isOpen ? 'opacity-100 w-auto' : 'opacity-0 w-0'}`}>
            <span className="text-xl font-bold text-[#ff4756] tracking-tighter whitespace-nowrap" style={{ fontFamily: "'montreal-serial-extrabold', sans-serif", textShadow: '0 0 20px rgba(255, 71, 86, 0.3)' }}>
              DASHBOARD
            </span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className={`flex-1 overflow-y-auto py-6 flex flex-col gap-2 ${isOpen ? 'px-4' : 'px-3 items-center'}`}>
        <p className={`text-[10px] uppercase font-semibold text-gray-500 tracking-widest mb-2 font-mono transition-all duration-300 ${isOpen ? 'px-4 opacity-100' : 'opacity-0 h-0 overflow-hidden mb-0'}`}>
          Operations
        </p>

        {items.map(item => {
          const isActive = activeId === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`
                  flex items-center min-h-[44px] rounded-xl text-sm font-medium transition-all group relative text-left
                  ${isOpen ? 'px-4 py-3 w-full gap-3' : 'w-12 h-12 justify-center gap-0'}
                  ${isActive ? 'bg-[#ff4756]/10 text-white' : 'text-gray-400 hover:text-white hover:bg-white/5'}
                `}
            >
              {/* Active Indicator Line */}
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-[#ff4756] rounded-r-full shadow-[0_0_8px_#ff4756]" />
              )}

              {/* Icon Container */}
              <div className={`relative z-10 transition-colors ${isActive ? 'text-[#ff4756]' : 'text-gray-500 group-hover:text-[#ff4756]/70'}`}>
                {item.icon}
              </div>

              {/* Label */}
              <span className={`relative z-10 tracking-wide transition-all duration-300 whitespace-nowrap font-normal ${isOpen ? 'opacity-100' : 'opacity-0 w-0'}`}>
                {item.label}
              </span>
            </button>
          );
        })}
      </nav>

      {/* User Profile Footer */}
      <div className={`p-6 border-t border-white/5 relative overflow-hidden group hover:bg-white/[0.02] transition-colors cursor-pointer flex justify-center`}>
        <div className={`flex items-center gap-3 relative z-10 ${isOpen ? 'w-full' : 'justify-center'}`}>
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shrink-0 border border-white/10 shadow-inner">
            <span className="text-sm font-bold text-white">AK</span>
          </div>
          <div className={`flex flex-col min-w-0 transition-all duration-300 overflow-hidden ${isOpen ? 'w-full opacity-100' : 'w-0 opacity-0'}`}>
            <span className="text-sm font-medium text-white truncate">Admin User</span>
            <span className="text-[10px] text-gray-500 truncate mt-0.5">admin@quant.net</span>
          </div>
          {isOpen && (
            <svg className="w-4 h-4 text-gray-500 shrink-0 ml-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
            </svg>
          )}
        </div>
      </div>
    </aside>
  );
};
