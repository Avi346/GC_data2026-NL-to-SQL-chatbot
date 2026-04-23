import { useState } from 'react';
import { useDashboardData } from './context/DashboardContext';
import { DashboardLayout } from './layout/DashboardLayout';
import { ExecutiveSummary } from './pages/ExecutiveSummary';
import { UsageTrends } from './pages/UsageTrends';
import { PublishingFunnel } from './pages/PublishingFunnel';
import { VideoExplorer } from './pages/VideoExplorer';
import { MediaHealth } from './pages/MediaHealth';
import { ContentIntelligence } from './pages/ContentIntelligence';
import { KnowledgeGraphPage } from './pages/KnowledgeGraph';
import { DataIngestion } from './pages/DataIngestion';

// SVG Icons for Navigation
const Icons = {
  Grid: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>,
  TrendingUp: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>,
  Filter: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" /></svg>,
  Users: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>,
  Shield: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>,
  Brain: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>,
  Share: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" /></svg>,
  Upload: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
};

const navItems = [
  { id: 'executive', label: 'Executive Summary', icon: Icons.Grid },
  { id: 'trends', label: 'Usage & Adoption', icon: Icons.TrendingUp },
  { id: 'funnel', label: 'Publishing Funnel', icon: Icons.Filter },
  { id: 'video', label: 'User Analytics', icon: Icons.Users },
  { id: 'health', label: 'Data Quality', icon: Icons.Shield },
  { id: 'intel', label: 'KPI Insights', icon: Icons.Brain },
  { id: 'graph', label: 'Platform Analytics', icon: Icons.Share },
  { id: 'ingestion', label: 'Data Ingestion', icon: Icons.Upload },
];

export default function App() {
  const [activePageId, setActivePageId] = useState('executive');

  const activeLabel = navItems.find(n => n.id === activePageId)?.label || '';

  const renderPage = () => {
    switch (activePageId) {
      case 'executive': return <ExecutiveSummary />;
      case 'trends': return <UsageTrends />;
      case 'funnel': return <PublishingFunnel />;
      case 'video': return <VideoExplorer />;
      case 'health': return <MediaHealth />;
      case 'intel': return <ContentIntelligence />;
      case 'graph': return <KnowledgeGraphPage />;
      case 'ingestion': return <DataIngestion />;
      default: return <ExecutiveSummary />;
    }
  };

  const { loading, error } = useDashboardData();

  if (loading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-[#09090b]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-[#ff4756]/30 border-t-[#ff4756] rounded-full animate-spin" />
          <span className="text-gray-400 font-medium tracking-wide">Loading Dashboard Data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-[#09090b]">
        <div className="text-rose-500 font-medium tracking-wide">Error loading data: {error}</div>
      </div>
    );
  }

  return (
    <DashboardLayout
      navItems={navItems}
      activeNavId={activePageId}
      onNavigate={setActivePageId}
      pageTitle={activeLabel}
    >
      {renderPage()}
    </DashboardLayout>
  );
}
