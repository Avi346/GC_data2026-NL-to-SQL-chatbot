import React from 'react';
import { GlassCard } from './GlassCard';
import type { InsightCard as InsightType } from '../types';

interface InsightCardProps {
  insight: InsightType;
}

export const InsightCard: React.FC<InsightCardProps> = ({ insight }) => {
  const isPositive = insight.type === 'positive';
  const isNegative = insight.type === 'negative';

  const accentColor = isPositive ? 'text-emerald-400' : isNegative ? 'text-rose-400' : 'text-amber-400';
  const glowColor = isPositive ? 'from-emerald-500/10' : isNegative ? 'from-rose-500/10' : 'from-amber-500/10';
  const badgeBg = isPositive ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' :
    isNegative ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' :
      'bg-amber-500/10 border-amber-500/20 text-amber-400';

  return (
    <GlassCard padding="md" interactive className="h-full flex flex-col relative overflow-hidden group">
      {/* Background tinted glow based on type */}
      <div className={`absolute -top-10 -right-10 w-40 h-40 bg-gradient-radial ${glowColor} to-transparent blur-2xl pointer-events-none opacity-50 group-hover:opacity-100 transition-opacity duration-700`} />

      {/* Icon and Title */}
      <div className="flex items-start gap-4 mb-4 relative z-10">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center bg-black/40 border border-white/5 shrink-0 shadow-lg ${accentColor}`}>
          {isPositive ? (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
          ) : isNegative ? (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>
          ) : (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          )}
        </div>
        <div className="flex-1">
          <h3 className="text-[15px] font-bold text-white tracking-tight leading-snug">{insight.title}</h3>
          <p className="text-[13px] text-gray-400 mt-1.5 leading-relaxed font-medium">
            {insight.description}
          </p>
        </div>
      </div>

      {/* Metric Badge (replaces sparkline) */}
      {insight.metric && insight.metricValue && (
        <div className="mt-auto pt-4 border-t border-white/[0.04] relative z-10">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase tracking-widest text-gray-500 font-mono">{insight.metric}</span>
            <span className={`px-3 py-1.5 rounded-lg border text-sm font-bold font-mono ${badgeBg}`}>
              {insight.metricValue}
            </span>
          </div>
        </div>
      )}
    </GlassCard>
  );
};
