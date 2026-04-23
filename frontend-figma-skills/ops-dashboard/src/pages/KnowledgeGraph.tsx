import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ZAxis, Cell } from 'recharts';
import { useDashboardData } from '../context/DashboardContext';
import { ChartCard } from '../components/ChartCard';
import { GlassCard } from '../components/GlassCard';
import { PieChart, Pie, Cell as PieCell } from 'recharts';

const platforms = ['Facebook', 'Instagram', 'LinkedIn', 'Reels', 'Shorts', 'X', 'YouTube', 'Threads'] as const;
const platformKeys = ['facebook', 'instagram', 'linkedin', 'reels', 'shorts', 'x', 'youtube', 'threads'] as const;

export const KnowledgeGraphPage: React.FC = () => {
  const { platformPublishData, scatterData, platformShareData, channelData } = useDashboardData();

  const getHeatmapColor = (val: number) => {
    if (val >= 15) return 'bg-[#ff4756] shadow-[0_0_12px_rgba(255,71,86,0.5)]';
    if (val >= 5) return 'bg-[#ff4756]/60';
    if (val >= 1) return 'bg-[#ff6d78]/40';
    if (val > 0) return 'bg-[#ffb7bc]/40';
    return 'bg-white/5';
  };

  // Only show channels that have at least 1 publication
  const activeChannels = platformPublishData.filter(ch => ch.total > 0);

  // Channel share data (X01)
  const totalPublished = channelData.reduce((s, c) => s + c.published, 0);
  const channelShareData = channelData
    .filter(c => c.published > 0)
    .sort((a, b) => b.published - a.published)
    .map(c => ({
      name: `Channel ${c.name}`,
      value: c.published,
      share: parseFloat(((c.published / totalPublished) * 100).toFixed(1)),
    }));

  return (
    <div className="space-y-8 pb-8 page-enter">

      {/* Channel-wise Platform Publishing Heatmap */}
      <ChartCard title="Channel × Platform Publishing Heatmap" subtitle="External publish count per channel per platform (D04)">
        <div className="overflow-x-auto pt-6 pb-2 px-2">
          <div className="min-w-[800px]">
            {/* Headers */}
            <div className="flex mb-4">
              <div className="w-32 shrink-0" />
              <div className="flex-1 flex justify-between gap-3">
                {platforms.map(p => (
                  <div key={p} className="flex-1 text-center text-[11px] font-semibold uppercase tracking-wider text-gray-400">
                    {p}
                  </div>
                ))}
              </div>
            </div>

            {/* Grid rows */}
            <div className="space-y-3">
              {activeChannels.map(ch => (
                <div key={ch.channel} className="flex items-center group">
                  <div className="w-32 shrink-0 text-[14px] font-medium text-gray-300 group-hover:text-[#ff4756] transition-colors">
                    Channel {ch.channel}
                    <span className="ml-2 text-[10px] text-gray-500 font-mono">({ch.total})</span>
                  </div>
                  <div className="flex-1 flex gap-3">
                    {platformKeys.map(pk => {
                      const val = ch[pk];
                      return (
                        <div key={`${ch.channel}-${pk}`} className="flex-1 relative group/cell">
                          <div className={`h-12 w-full rounded-xl transition-all duration-300 border border-white/5 cursor-crosshair flex items-center justify-center ${getHeatmapColor(val)}`}>
                            {val > 0 && <span className="text-xs font-bold text-white/80">{val}</span>}
                          </div>

                          <div className="absolute -top-12 left-1/2 -translate-x-1/2 px-4 py-2 bg-gray-900 border border-white/10 rounded-lg shadow-xl text-sm text-white opacity-0 group-hover/cell:opacity-100 transition-opacity pointer-events-none z-50 whitespace-nowrap font-medium">
                            <span className="text-[#ff4756] font-bold">{val}</span> published
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </ChartCard>

      {/* Bottom row: Scatter + Channel Share */}
      <div className="grid lg:grid-cols-2 gap-10">
        {/* Volume vs Publish Output Scatter (X02) */}
        <div className="h-[450px]">
          <ChartCard title="Volume vs. Publish Scatter" subtitle="Created Count (x) vs Published Count (y) · Bubble = √Uploads (X02)" badge="X02">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 30, left: 10, bottom: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis
                  dataKey="x" type="number" name="Created"
                  tick={{ fill: '#9ca3af', fontSize: 11 }} axisLine={false} tickLine={false}
                  label={{ value: 'AI Created Count', position: 'bottom', fill: '#6b7280', fontSize: 12, dy: 15 }}
                />
                <YAxis
                  dataKey="y" type="number" name="Published"
                  tick={{ fill: '#9ca3af', fontSize: 11 }} axisLine={false} tickLine={false}
                  label={{ value: 'Published Count', angle: -90, position: 'insideLeft', fill: '#6b7280', fontSize: 12, dx: -5 }}
                />
                <ZAxis dataKey="z" range={[40, 400]} />
                <Tooltip
                  contentStyle={{ background: 'rgba(9,9,11,0.95)', backdropFilter: 'blur(16px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px', fontWeight: 500 }}
                  formatter={(v: any, name: any) => [v, name]}
                  labelFormatter={(_, payload) => {
                    if (payload && payload[0]) {
                      const d = payload[0].payload;
                      return `${d.name} · Rate: ${d.publishRate}%`;
                    }
                    return '';
                  }}
                />
                <Scatter data={scatterData} shape="circle">
                  {scatterData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} fillOpacity={0.7} stroke={entry.color} strokeWidth={2} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* Channel Share in Published Output (X01) + Platform Share (D04) */}
        <div className="space-y-6">
          {/* Channel Share */}
          <GlassCard padding="lg">
            <h3 className="text-base font-semibold text-white tracking-tight mb-4">Channel Share in Published Output (X01)</h3>
            <div className="flex items-center gap-6">
              <div className="w-40 h-40 shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={channelShareData} cx="50%" cy="50%" innerRadius="50%" outerRadius="80%" paddingAngle={3} dataKey="value" stroke="rgba(0,0,0,0.5)" strokeWidth={2}>
                      {channelShareData.map((_, i) => {
                        const colors = ['#ff4756', '#ff6d78', '#ff8a94', '#ffb7bc', '#ffd1d4', '#34d399'];
                        return <PieCell key={i} fill={colors[i % colors.length]} />;
                      })}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex-1 space-y-2">
                {channelShareData.map((ch, i) => {
                  const colors = ['#ff4756', '#ff6d78', '#ff8a94', '#ffb7bc', '#ffd1d4', '#34d399'];
                  const isCritical = ch.share > 60;
                  return (
                    <div key={ch.name} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: colors[i % colors.length] }} />
                        <span className="text-sm text-gray-300">{ch.name}</span>
                      </div>
                      <span className={`text-sm font-bold font-mono ${isCritical ? 'text-rose-400' : 'text-gray-200'}`}>{ch.share}%</span>
                    </div>
                  );
                })}
              </div>
            </div>
            <div className="mt-4 pt-3 border-t border-white/5">
              <p className="text-[10px] text-rose-400 font-semibold">⚠ Channel A commands 64% — critical concentration risk</p>
            </div>
          </GlassCard>

          {/* Platform Volume Share */}
          <GlassCard padding="lg">
            <h3 className="text-base font-semibold text-white tracking-tight mb-4">Platform Publish Volume Share (D04)</h3>
            <div className="space-y-3">
              {platformShareData.map(p => {
                const totalPlatform = platformShareData.reduce((s, x) => s + x.value, 0);
                const pct = ((p.value / totalPlatform) * 100).toFixed(1);
                return (
                  <div key={p.name} className="flex items-center gap-3">
                    <span className="w-20 text-sm text-gray-400 shrink-0">{p.name}</span>
                    <div className="flex-1 h-5 bg-white/5 rounded-lg overflow-hidden">
                      <div className="h-full rounded-lg" style={{ width: `${pct}%`, backgroundColor: p.color }} />
                    </div>
                    <span className="text-sm font-mono text-gray-300 w-12 text-right">{p.value}</span>
                    <span className="text-xs font-mono text-gray-500 w-12 text-right">{pct}%</span>
                  </div>
                );
              })}
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
};
