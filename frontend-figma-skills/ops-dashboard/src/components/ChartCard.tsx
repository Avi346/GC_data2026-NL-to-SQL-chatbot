import React from 'react';
import { GlassCard } from './GlassCard';

interface ChartCardProps {
  title: string;
  subtitle?: string;
  badge?: string;
  children: React.ReactNode;
  glow?: boolean;
}

export const ChartCard: React.FC<ChartCardProps> = ({
  title,
  subtitle,
  badge,
  children,
  glow = false
}) => {
  return (
    <GlassCard padding="md" glow={glow} className="h-full flex flex-col">
      {/* Chart Header - Consistent Spacing via flex & mb-6 */}
      <div className="flex items-start justify-between mb-6 relative z-10">
        <div>
          <h2 className="text-sm font-semibold text-gray-200 tracking-tight">{title}</h2>
          {subtitle && (
            <p className="text-[10px] text-gray-500 mt-1 uppercase tracking-wider font-semibold">{subtitle}</p>
          )}
        </div>
        
        {badge && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#ff4756]/10 border border-[#ff4756]/20">
            <span className="w-1.5 h-1.5 rounded-full bg-[#ff4756] animate-pulse" />
            <span className="text-[10px] uppercase font-mono tracking-wider text-[#ff4756] font-semibold">{badge}</span>
          </div>
        )}
      </div>
      
      {/* Chart Body - takes remaining space */}
      <div className="flex-1 w-full relative z-10 min-h-[200px]">
        {children}
      </div>
    </GlassCard>
  );
};
