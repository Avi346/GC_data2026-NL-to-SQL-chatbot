import React from 'react';
import { GlassCard } from './GlassCard';
import type { KPIMetric } from '../types';

interface KpiCardProps {
  kpi: KPIMetric;
  interactive?: boolean;
}

export const KpiCard: React.FC<KpiCardProps> = ({ kpi, interactive = true }) => {
  const isUp = kpi.trend === 'up';
  const isDown = kpi.trend === 'down';
  
  // Specific styling based on trend
  const trendColor = isUp ? 'text-emerald-400' : isDown ? 'text-rose-400' : 'text-gray-500';
  const trendSign = isUp ? '+' : isDown ? '-' : '';

  return (
    <GlassCard padding="md" interactive={interactive} className="@container group">
      {/* Subtle hover background logic handled by glass-interactive, but we add a custom glow here */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#ff4756]/0 to-[#ff4756]/0 group-hover:from-[#ff4756]/[0.04] group-hover:to-transparent transition-all duration-500 pointer-events-none" />
      
      <div className="flex flex-col gap-4 relative z-10 w-full h-full">
        {/* Label section */}
        <div className="flex items-center justify-between">
          <h3 className="text-[10px] @[17.5rem]:text-xs uppercase tracking-widest text-gray-400 font-medium transition-all">
            {kpi.label}
          </h3>
          {/* Trend Indicator Icon */}
          <div className={`w-8 h-8 rounded-full flex items-center justify-center bg-white/5 border border-white/5 ${trendColor} transition-colors duration-300 shadow-[0_0_12px_rgba(0,0,0,0.3)]`}>
             {isUp || isDown ? (
               <svg 
                  className={`w-4 h-4 ${isDown ? 'rotate-180' : ''}`} 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                </svg>
             ) : (
               <svg 
                  className="w-4 h-4" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 16v-5m0-4h.01" />
                </svg>
             )}
          </div>
        </div>
        
        {/* Value and Delta Section */}
        <div className="flex items-end gap-2 @[17.5rem]:gap-3">
          <span className="text-2xl @[17.5rem]:text-3xl font-bold text-white tracking-tight leading-none transition-all">
            {kpi.value}
          </span>
          
          {kpi.delta !== undefined && (
            <div className="hidden @[17.5rem]:flex items-center gap-1 mb-0.5">
              <div className={`flex items-center pb-1 ${trendColor}`}>
                <span className="text-sm font-semibold tracking-wide">
                  {trendSign}{Math.abs(kpi.delta)}%
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </GlassCard>
  );
};
