import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, CartesianGrid } from 'recharts';
import { useDashboardData } from '../context/DashboardContext';
import { KpiCard } from '../components/KpiCard';
import { ChartCard } from '../components/ChartCard';
import { GlassCard } from '../components/GlassCard';

export const ExecutiveSummary: React.FC = () => {
  const { kpiMetrics, monthlyData, inputMixData, outputMixData, channelData } = useDashboardData();

  // Upload volume trend data for the area chart
  const trendData = monthlyData.map(d => ({ month: d.month, value: d.uploaded }));

  // Channel data sorted by published descending for scorecards
  const topChannels = [...channelData].sort((a, b) => b.published - a.published).slice(0, 6);

  return (
    <div className="flex flex-col gap-10 pb-12 page-enter">

      {/* KPIs Grid - 4x2 */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiMetrics.map((kpi) => (
          <KpiCard key={kpi.id} kpi={kpi} />
        ))}
      </section>

      {/* Main Trend Chart - Upload Volume Trend (A01) */}
      <section className="h-[450px]">
        <ChartCard title="Upload Volume Trend" subtitle="Monthly uploads · Mar 2025 – Feb 2026" badge="A01" glow>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trendData} margin={{ top: 20, right: 20, left: 0, bottom: 30 }}>
              <defs>
                <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ff4756" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="#ff4756" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{ fill: '#6b7280', fontSize: 12, fontWeight: 500 }} axisLine={false} tickLine={false} dy={16} />
              <YAxis tick={{ fill: '#6b7280', fontSize: 12, fontWeight: 500 }} axisLine={false} tickLine={false} dx={-10} width={40} />
              <Tooltip
                contentStyle={{
                  background: 'rgba(9, 9, 11, 0.95)',
                  backdropFilter: 'blur(24px)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '16px',
                  fontSize: '13px',
                  fontWeight: 500,
                  color: '#f3f4f6',
                  boxShadow: '0 10px 40px -10px rgba(255,71,86,0.2)',
                  padding: '12px 16px'
                }}
                itemStyle={{ color: '#ff4756', fontWeight: 600 }}
              />
              <Area type="monotone" dataKey="value" stroke="#ff4756" strokeWidth={3} fill="url(#trendGrad)" activeDot={{ r: 8, fill: '#000', stroke: '#ff4756', strokeWidth: 3 }} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
      </section>

      {/* Mix Charts Grid */}
      <section className="grid lg:grid-cols-2 gap-10 h-[380px]">
        <ChartCard title="Input Type Distribution" subtitle="By Content Category (B02)">
          <div className="flex h-full items-center justify-between p-4">
            <ResponsiveContainer width="45%" height="100%">
              <PieChart>
                <Pie data={inputMixData} cx="50%" cy="50%" innerRadius="55%" outerRadius="80%" paddingAngle={4} dataKey="value" stroke="rgba(0,0,0,0.5)" strokeWidth={3}>
                  {inputMixData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ background: 'rgba(9,9,11,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '13px', color: '#f3f4f6', fontWeight: 500 }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1 flex flex-col justify-center gap-4 pl-6 border-l border-white/[0.05]">
              {inputMixData.map((item) => (
                <div key={item.name} className="flex justify-between items-center group">
                  <div className="flex items-center gap-4">
                    <div className="relative w-3 h-3 shrink-0">
                      <div className="absolute inset-0 rounded-full opacity-50 blur-[4px]" style={{ backgroundColor: item.color }} />
                      <div className="absolute inset-0 rounded-full ring-2 ring-white/10" style={{ backgroundColor: item.color }} />
                    </div>
                    <span className="text-[15px] font-medium text-gray-400 group-hover:text-white transition-colors">{item.name}</span>
                  </div>
                  <span className="text-[15px] text-gray-200 font-semibold tracking-wide">{item.value.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>
        </ChartCard>

        <ChartCard title="Output Type Distribution" subtitle="By AI Output Type (B01)">
          <div className="flex h-full items-center justify-between p-4">
            <ResponsiveContainer width="45%" height="100%">
              <PieChart>
                <Pie data={outputMixData} cx="50%" cy="50%" innerRadius="55%" outerRadius="80%" paddingAngle={4} dataKey="value" stroke="rgba(0,0,0,0.5)" strokeWidth={3}>
                  {outputMixData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ background: 'rgba(9,9,11,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '13px', color: '#f3f4f6', fontWeight: 500 }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1 flex flex-col justify-center gap-4 pl-6 border-l border-white/[0.05]">
              {outputMixData.map((item) => (
                <div key={item.name} className="flex justify-between items-center group">
                  <div className="flex items-center gap-4">
                    <div className="relative w-3 h-3 shrink-0">
                      <div className="absolute inset-0 rounded-full opacity-50 blur-[4px]" style={{ backgroundColor: item.color }} />
                      <div className="absolute inset-0 rounded-full ring-2 ring-white/10" style={{ backgroundColor: item.color }} />
                    </div>
                    <span className="text-[15px] font-medium text-gray-400 group-hover:text-white transition-colors">{item.name}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-[11px] font-mono text-gray-500">{item.publishRate}%</span>
                    <span className="text-[15px] text-gray-200 font-semibold tracking-wide">{item.value.toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </ChartCard>
      </section>

      {/* Channel Scorecards */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-bold text-white tracking-tight">Channel Performance Overview</h2>
          <span className="text-xs text-gray-500 font-mono tracking-widest uppercase">{channelData.length} total channels · {channelData.filter(c => c.published > 0).length} publishers</span>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {topChannels.map(ch => {
            const isPublisher = ch.published > 0;
            const statusColor = ch.publishRate >= 1 ? '#34d399' : ch.publishRate > 0 ? '#fbbf24' : '#f43f5e';
            const statusLabel = ch.publishRate >= 1 ? 'active publisher' : ch.publishRate > 0 ? 'low publish' : 'zero publisher';
            const gaugeVal = Math.min(ch.publishRate * 20, 100); // Scale for visual gauge

            return (
              <GlassCard key={ch.name} interactive padding="lg" className="group flex flex-col h-full">
                <div className="flex items-start justify-between mb-6 relative z-10">
                  <div>
                    <h3 className="text-base font-bold text-white group-hover:text-[#ff4756] transition-colors">Channel {ch.name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="relative w-1.5 h-1.5 shrink-0">
                        <div className="absolute inset-0 rounded-full opacity-60 blur-[3px]" style={{ backgroundColor: statusColor }} />
                        <div className="absolute inset-0 rounded-full" style={{ backgroundColor: statusColor }} />
                      </div>
                      <span className="text-[10px] uppercase tracking-widest font-mono" style={{ color: statusColor }}>{statusLabel}</span>
                    </div>
                  </div>

                  {/* Radial Gauge */}
                  <div className="relative w-14 h-14 shrink-0">
                    <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90 overflow-visible">
                      <circle cx="18" cy="18" r="15" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="4" />
                      <circle cx="18" cy="18" r="15" fill="none" stroke={statusColor} strokeWidth="4"
                        strokeDasharray={`${(gaugeVal / 100) * 94.25} 94.25`} strokeLinecap="round"
                        className="transition-all duration-1000 ease-out opacity-40 blur-[3px]"
                      />
                      <circle cx="18" cy="18" r="15" fill="none" stroke={statusColor} strokeWidth="4"
                        strokeDasharray={`${(gaugeVal / 100) * 94.25} 94.25`} strokeLinecap="round"
                        className="transition-all duration-1000 ease-out"
                      />
                    </svg>
                    <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-white font-mono">{ch.publishRate}%</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-y-6 gap-x-6 border-t border-white/5 pt-6 mt-auto relative z-10">
                  <div>
                    <p className="text-[11px] uppercase text-gray-500 font-bold tracking-wider mb-1.5">Uploaded</p>
                    <p className="text-lg font-bold text-gray-200">{ch.uploaded.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-[11px] uppercase text-gray-500 font-bold tracking-wider mb-1.5">AI Created</p>
                    <p className="text-lg font-bold text-gray-200">{ch.created.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-[11px] uppercase text-gray-500 font-bold tracking-wider mb-1.5">Published</p>
                    <p className="text-lg font-bold text-gray-300">{isPublisher ? ch.published.toLocaleString() : '—'}</p>
                  </div>
                  <div>
                    <p className="text-[11px] uppercase text-gray-500 font-bold tracking-wider mb-1.5">Publish Rate</p>
                    <p className="text-lg font-bold" style={{ color: statusColor }}>{ch.publishRate}%</p>
                  </div>
                </div>
              </GlassCard>
            );
          })}
        </div>
      </section>
    </div>
  );
};
