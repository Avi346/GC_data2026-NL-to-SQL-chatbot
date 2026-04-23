import React from 'react';
import { GlassCard } from '../components/GlassCard';

// Data Quality KPIs from Section E
const dataQualityMetrics = [
  {
    id: 'field-completeness',
    label: 'Field Completeness (E01)',
    sublabel: 'Team Name Field',
    value: '0.71%',
    status: 'critical' as const,
    detail: 'Only 106 of 14,918 records have a valid team name. Team-level reporting is impossible.',
    recommendation: 'Require teams to set workspace team name during channel setup.',
    trendData: [0.5, 0.6, 0.7, 0.65, 0.7, 0.71, 0.71],
  },
  {
    id: 'unknown-rate',
    label: 'Unknown / Placeholder Rate (E02)',
    sublabel: 'Team Name Field',
    value: '99.3%',
    status: 'critical' as const,
    detail: '14,779 of 14,885 non-null Team Name values are the placeholder "Unknown". Functionally useless.',
    recommendation: 'Build an automated Unknown Rate monitor. Flag any field crossing 20%.',
    trendData: [99.5, 99.4, 99.3, 99.3, 99.3, 99.3, 99.3],
  },
  {
    id: 'duplicate-rate',
    label: 'Duplicate Record Rate (E03)',
    sublabel: 'Video ID Duplicates',
    value: '0.033%',
    status: 'ok' as const,
    detail: '5 Video IDs appear more than once across 14,918 records. Very low, but duplicates can corrupt funnel metrics.',
    recommendation: 'Add deduplication step (keep latest record per Video ID) to all ETL pipelines.',
    trendData: [0.04, 0.035, 0.033, 0.033, 0.033, 0.033, 0.033],
  },
];

// Additional field completeness breakdown
const fieldCompleteness = [
  { field: 'Video ID', completeness: 99.97, status: 'ok' },
  { field: 'Channel', completeness: 100, status: 'ok' },
  { field: 'Input Type', completeness: 99.7, status: 'ok' },
  { field: 'Output Type', completeness: 100, status: 'ok' },
  { field: 'Language', completeness: 99.5, status: 'ok' },
  { field: 'Published Status', completeness: 100, status: 'ok' },
  { field: 'Published Platform', completeness: 0.22, status: 'critical' },
  { field: 'Published URL', completeness: 0.15, status: 'critical' },
  { field: 'Team Name', completeness: 0.71, status: 'critical' },
  { field: 'Upload Duration', completeness: 98.2, status: 'ok' },
];

export const MediaHealth: React.FC = () => {
  return (
    <div className="space-y-8 pb-8 page-enter">

      {/* Health Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {dataQualityMetrics.map(metric => {
          const isCritical = metric.status === 'critical';

          const glowColor = isCritical ? 'from-rose-500/20 via-rose-500/5 to-transparent' :
            'from-emerald-500/10 via-emerald-500/5 to-transparent';

          const statusLabel = isCritical ? 'CRITICAL' : 'HEALTHY';

          return (
            <GlassCard key={metric.id} padding="lg" interactive className="@container">
              <div className={`absolute top-0 right-0 w-64 h-64 bg-gradient-radial ${glowColor} blur-2xl pointer-events-none rounded-bl-full`} />

              <div className="flex flex-col relative z-10 h-full">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-[11px] @[17.5rem]:text-sm font-semibold text-gray-200 tracking-wide transition-all">{metric.label}</h3>
                    <p className="text-[10px] text-gray-500 mt-0.5">{metric.sublabel}</p>
                    <div className="flex items-center gap-2 mt-2.5">
                      <span className={`w-2 h-2 rounded-full ${isCritical ? 'bg-rose-500 shadow-[0_0_8px_#f43f5e] animate-pulse' : 'bg-emerald-500'}`} />
                      <span className={`text-[10px] @[17.5rem]:text-[11px] uppercase font-bold tracking-widest transition-all ${isCritical ? 'text-rose-400' : 'text-emerald-400'}`}>
                        {statusLabel}
                      </span>
                    </div>
                  </div>
                  <span className={`text-2xl @[17.5rem]:text-3xl font-bold tracking-tight drop-shadow-md transition-all ${isCritical ? 'text-rose-400' : 'text-emerald-400'}`}>{metric.value}</span>
                </div>

                <p className="text-xs text-gray-400 leading-relaxed mb-3">{metric.detail}</p>

                <div className="mt-auto pt-3 border-t border-white/5">
                  <p className="text-[10px] text-gray-500 uppercase font-semibold tracking-wider mb-1">Recommendation</p>
                  <p className="text-xs text-gray-300">{metric.recommendation}</p>
                </div>
              </div>
            </GlassCard>
          );
        })}
      </div>

      {/* Field Completeness Breakdown */}
      <GlassCard padding="lg" className="h-auto">
        <h2 className="text-base font-semibold text-white tracking-tight mb-6">Field Completeness Breakdown (E01)</h2>
        <div className="space-y-3">
          {fieldCompleteness.map((field) => {
            const isCritical = field.status === 'critical';
            const barColor = isCritical ? '#f43f5e' : '#34d399';
            return (
              <div key={field.field} className="flex items-center gap-4 group">
                <span className="w-36 text-sm text-gray-300 font-medium shrink-0 group-hover:text-white transition-colors">{field.field}</span>
                <div className="flex-1 h-6 bg-white/5 rounded-lg overflow-hidden relative">
                  <div
                    className="h-full rounded-lg transition-all duration-700"
                    style={{ width: `${Math.max(field.completeness, 1)}%`, backgroundColor: barColor, opacity: isCritical ? 1 : 0.6 }}
                  />
                  {isCritical && (
                    <div className="absolute inset-0 flex items-center px-3">
                      <span className="text-[10px] font-bold text-rose-300">{field.completeness}%</span>
                    </div>
                  )}
                </div>
                <span className={`text-sm font-mono w-16 text-right ${isCritical ? 'text-rose-400 font-bold' : 'text-gray-500'}`}>
                  {field.completeness}%
                </span>
              </div>
            );
          })}
        </div>
      </GlassCard>

      {/* Data Quality Summary */}
      <GlassCard padding="lg">
        <h2 className="text-base font-semibold text-white tracking-tight mb-4">Data Governance Summary</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="p-4 rounded-xl border border-white/5 bg-white/[0.02]">
            <p className="text-[10px] uppercase tracking-widest text-gray-500 font-mono mb-2">Total Records</p>
            <p className="text-2xl font-bold text-white">14,918</p>
          </div>
          <div className="p-4 rounded-xl border border-rose-500/20 bg-rose-500/5">
            <p className="text-[10px] uppercase tracking-widest text-gray-500 font-mono mb-2">Critical Fields</p>
            <p className="text-2xl font-bold text-rose-400">3 <span className="text-sm text-gray-500">fields below 1%</span></p>
          </div>
          <div className="p-4 rounded-xl border border-emerald-500/20 bg-emerald-500/5">
            <p className="text-[10px] uppercase tracking-widest text-gray-500 font-mono mb-2">Healthy Fields</p>
            <p className="text-2xl font-bold text-emerald-400">7 <span className="text-sm text-gray-500">fields above 98%</span></p>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};
