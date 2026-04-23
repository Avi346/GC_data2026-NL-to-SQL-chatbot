import React, { useState } from 'react';
import { Sidebar, type NavItem } from './Sidebar';
import { Navbar } from './Navbar';
import { ChatPanel } from './ChatPanel';

const API_BASE = 'http://localhost:8000';

interface DashboardLayoutProps {
  children: React.ReactNode;
  navItems: NavItem[];
  activeNavId: string;
  onNavigate: (id: string) => void;
  pageTitle: string;
}

  export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ 
    children, 
    navItems, 
    activeNavId, 
    onNavigate,
    pageTitle
  }) => {
    const [isChatOpen, setIsChatOpen] = useState(false);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [appMode, setAppMode] = useState<'admin' | 'user'>('admin');

    const apiPrefix = appMode === 'admin' ? '/api/admin' : '/api/user';
  
    return (
      <div className="flex h-screen w-full bg-black overflow-hidden selection:bg-[#ff4756]/30">
        {/* Global Background Elements */}
        <div className="fixed inset-0 z-0 pointer-events-none">
          {/* Subtle noise texture overlay */}
          <div className="absolute inset-0 opacity-[0.015]" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.65%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E")' }}></div>
          {/* Ambient glows */}
          <div className="absolute top-[10%] left-[20%] w-[500px] h-[500px] bg-cyan-600/10 rounded-full blur-[120px]" />
          <div className="absolute bottom-[10%] right-[30%] w-[600px] h-[600px] bg-indigo-600/10 rounded-full blur-[150px]" />
        </div>
  
        <Sidebar 
          items={navItems} 
          activeId={activeNavId} 
          onNavigate={onNavigate} 
          isOpen={isSidebarOpen} 
          onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        />
  
        <div className="flex-1 flex flex-col h-full min-w-0 relative z-10 transition-all">
          <Navbar appMode={appMode} onModeChange={setAppMode} />
          
          {/* Main Content Scroll Area */}
          <main className="flex-1 overflow-x-hidden overflow-y-auto relative">
            <div className="w-full max-w-[1600px] mx-auto p-8 lg:p-10 page-enter">
              <div className="mb-8">
                <h1 className="text-2xl font-bold text-white tracking-tight">{pageTitle}</h1>
                <div className="h-1 w-10 bg-gradient-to-r from-[#ff4756] to-[#ffb7bc] rounded-full mt-4 shadow-[0_0_8px_rgba(255,71,86,0.4)]" />
              </div>
              {children}
            </div>
          </main>
        </div>
  
        {isChatOpen && <ChatPanel onClose={() => setIsChatOpen(false)} apiBase={API_BASE} apiPrefix={apiPrefix} appMode={appMode} />}
        
        {/* Floating AI Assistant Toggle Button */}
        {!isChatOpen && (
          <button
            onClick={() => setIsChatOpen(!isChatOpen)}
            className="fixed bottom-8 right-8 z-50 w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 bg-black/80 backdrop-blur-md border border-white/10 text-[#ff4756] hover:bg-black hover:border-[#ff4756]/50 shadow-[0_0_15px_rgba(0,0,0,0.5)]"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </button>
        )}
      </div>
    );
  };
