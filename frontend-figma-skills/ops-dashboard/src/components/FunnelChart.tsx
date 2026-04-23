import React from 'react';
import type { FunnelStep } from '../types';

interface FunnelChartProps {
  data: FunnelStep[];
}

export const FunnelChart: React.FC<FunnelChartProps> = ({ data }) => {
  if (!data || data.length === 0) return null;
  const maxVal = Math.max(...data.map(d => d.value));

  return (
    <div className="w-full flex justify-center py-4">
      <div className="w-full max-w-4xl flex flex-col gap-3">
        {data.map((step, i) => {
          const isFirst = i === 0;
          const diff = !isFirst ? step.value - data[i - 1].value : 0;
          const diffPct = !isFirst ? (Math.abs(diff) / data[i - 1].value * 100).toFixed(1) : 0;
          const isGrowth = diff > 0;
          const percentageOfTotal = (step.value / maxVal * 100).toFixed(1);
          
          return (
            <React.Fragment key={step.id}>
              {/* Connector / Indicator */}
              {!isFirst && (
                <div className="flex justify-center -my-1">
                  <div className={`px-4 py-1 rounded-full text-[10px] font-bold tracking-widest uppercase flex items-center gap-2 border ${
                    isGrowth 
                      ? 'bg-emerald-500/5 border-emerald-500/10 text-emerald-400' 
                      : 'bg-rose-500/5 border-rose-500/10 text-rose-400'
                  }`}>
                    <span className="opacity-50">{isGrowth ? '▲' : '▼'}</span>
                    {isGrowth ? '+' : '-'}{diffPct}% {isGrowth ? 'Volume Growth' : 'Funnel Drop-off'}
                  </div>
                </div>
              )}

              {/* Step Row */}
              <div className="relative group">
                <div className="h-16 glass-panel border border-white/[0.08] rounded-2xl overflow-hidden flex items-center px-6 relative transition-all group-hover:border-white/[0.15]">
                  {/* Subtle Volume Indicator (Internal Bar) */}
                  <div 
                    className="absolute inset-y-0 left-0 bg-white/[0.03] transition-all duration-1000 ease-out border-r border-white/5"
                    style={{ 
                      width: `${percentageOfTotal}%`,
                      background: `linear-gradient(90deg, ${step.color}40, ${step.color}80)`
                    }}
                  />
                  
                  {/* Container Content */}
                  <div className="relative z-10 w-full flex items-center justify-between gap-10">
                    <div className="flex items-center gap-5 shrink-0">
                      <div className="w-8 h-8 rounded-xl bg-black/40 border border-white/5 flex items-center justify-center text-[10px] font-bold text-gray-500 font-mono">
                        0{i+1}
                      </div>
                      <span className="text-[15px] font-semibold text-gray-200 tracking-tight group-hover:text-white transition-colors">
                        {step.label}
                      </span>
                    </div>

                    <div className="flex items-baseline gap-4">
                      <div className="flex flex-col items-end">
                        <span className="text-xl font-bold text-white tracking-tight font-mono leading-none">
                          {step.value.toLocaleString()}
                        </span>
                        <span className="text-[10px] font-bold text-[#ff4756]/60 font-mono mt-1 tracking-wider uppercase">
                          {percentageOfTotal}% <span className="text-gray-600">Index</span>
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
