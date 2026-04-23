import React from 'react';
import { useDashboardData } from '../context/DashboardContext';
import { InsightCard } from '../components/InsightCard';
import { GlassCard } from '../components/GlassCard';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { ChartCard } from '../components/ChartCard';

export const ContentIntelligence: React.FC = () => {
  const { insightsData, benchmarkKPIs, languageData } = useDashboardData();

  // Language publish rate chart data (D03)
  const langChartData = languageData
    .filter(l => l.created > 0)
    .map(l => ({
      name: l.language,
      rate: l.publishRate,
      published: l.published,
      created: l.created,
    }));

  return (
    <div className="space-y-8 pb-8 page-enter">

      {/* Benchmark Dashboard */}
      <GlassCard padding="lg" className="relative group overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#ff4756]/5 via-transparent to-[#ff4756]/5" />
        <div className="absolute top-0 right-0 w-full h-full bg-[radial-gradient(ellipse_at_top_right,rgba(255,71,86,0.1)_0%,transparent_50%)] opacity-50 group-hover:opacity-100 transition-opacity duration-1000 pointer-events-none" />

        <div className="relative z-10">
          <h2 className="text-xl font-bold text-white tracking-tight mb-2">KPI Health Benchmarks</h2>
          <p className="text-sm text-gray-400 leading-relaxed mb-6 max-w-3xl">
            Real-time status of 7 core benchmarks against industry thresholds. Data source: CLIENT_1 anonymised dataset · 18 channels · 14,918 video records.
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {benchmarkKPIs.map(kpi => {
              const colors = {
                healthy: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', text: 'text-emerald-400', dot: 'bg-emerald-500' },
                concerning: { bg: 'bg-amber-500/10', border: 'border-amber-500/20', text: 'text-amber-400', dot: 'bg-amber-500' },
                critical: { bg: 'bg-rose-500/10', border: 'border-rose-500/20', text: 'text-rose-400', dot: 'bg-rose-500 animate-pulse shadow-[0_0_8px_#f43f5e]' },
              };
              const c = colors[kpi.status];

              return (
                <div key={kpi.id} className={`p-4 rounded-xl border ${c.border} ${c.bg} transition-all hover:scale-[1.02]`}>
                  <div className="flex items-center gap-2 mb-3">
                    <span className={`w-2 h-2 rounded-full ${c.dot}`} />
                    <span className={`text-[10px] uppercase font-bold tracking-widest ${c.text}`}>{kpi.status}</span>
                  </div>
                  <p className="text-[11px] text-gray-400 font-medium mb-1">{kpi.label}</p>
                  <p className={`text-2xl font-bold ${c.text} tracking-tight`}>{kpi.displayValue}</p>
                  <div className="mt-3 pt-3 border-t border-white/5">
                    <div className="flex gap-2 text-[9px] font-mono text-gray-500">
                      <span className="text-emerald-500">✓ {kpi.thresholds.healthy}</span>
                      <span className="text-amber-500">⚠ {kpi.thresholds.concerning}</span>
                      <span className="text-rose-500">✗ {kpi.thresholds.critical}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </GlassCard>

      {/* Grid of Insight Cards */}
      <div>
        <h2 className="text-lg font-bold text-white tracking-tight mb-4">Actionable Insights</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {insightsData.map(insight => (
            <InsightCard key={insight.id} insight={insight} />
          ))}
        </div>
      </div>

      {/* Language Publish Rate (D03) */}
      <div className="h-[380px]">
        <ChartCard title="Language Publish Rate" subtitle="Publishing conversion by content language (D03)">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={langChartData} layout="vertical" margin={{ top: 20, right: 30, left: 10, bottom: 20 }} barSize={28}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" tick={{ fill: '#9ca3af', fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v}%`} />
              <YAxis dataKey="name" type="category" tick={{ fill: '#d1d5db', fontSize: 13, fontWeight: 500 }} axisLine={false} tickLine={false} width={110} />
              <Tooltip
                contentStyle={{ background: 'rgba(9,9,11,0.95)', backdropFilter: 'blur(16px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px', fontWeight: 500 }}
                formatter={(v: any, _: any, entry: any) => [`${v}% (${entry.payload.published} of ${entry.payload.created})`, 'Publish Rate']}
              />
              <Bar dataKey="rate" fill="#ff4756" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
};
