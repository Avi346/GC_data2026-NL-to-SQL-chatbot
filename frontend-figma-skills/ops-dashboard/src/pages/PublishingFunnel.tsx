import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { useDashboardData } from '../context/DashboardContext';
import { ChartCard } from '../components/ChartCard';
import { FunnelChart } from '../components/FunnelChart';
import { GlassCard } from '../components/GlassCard';

export const PublishingFunnel: React.FC = () => {
  const { funnelData, outputTypeData, channelData, PUBLISH_RATE, PUBLISH_GAP } = useDashboardData();

  // Publish rate by output type (horizontal bar)
  const outputRateData = outputTypeData.map(d => ({
    name: d.name,
    rate: d.publishRate,
    published: d.published,
    created: d.created,
  })).sort((a, b) => b.rate - a.rate);

  // Channel publish rate (top 10 channels by created count)
  const channelRateData = [...channelData]
    .sort((a, b) => b.created - a.created)
    .slice(0, 10)
    .map(ch => ({
      name: `Ch ${ch.name}`,
      rate: ch.publishRate,
      published: ch.published,
      created: ch.created,
    }));

  return (
    <div className="space-y-8 pb-8 page-enter">

      {/* Top Level Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <GlassCard padding="lg" interactive className="@container">
          <div className="flex items-center gap-5">
            <div className="w-12 h-12 rounded-full bg-[#ff4756]/10 border border-[#ff4756]/20 flex items-center justify-center shrink-0">
              <svg className="w-6 h-6 text-[#ff4756]" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] @[17.5rem]:text-[11px] font-semibold tracking-wider text-gray-400 uppercase mb-1 transition-all">Total Uploaded</span>
              <span className="text-xl @[17.5rem]:text-2xl font-bold text-white tracking-tight transition-all">4,453</span>
            </div>
          </div>
        </GlassCard>

        <GlassCard padding="md" className="flex items-center gap-5 group @container">
          <div className="w-12 h-12 rounded-full bg-[#ff6d78]/10 border border-[#ff6d78]/20 flex items-center justify-center shrink-0 group-hover:bg-[#ff6d78]/20 transition-colors">
            <svg className="w-5 h-5 text-[#ff6d78]" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
          <div className="flex-1">
            <div className="flex flex-col">
              <span className="text-[10px] @[17.5rem]:text-[11px] font-semibold tracking-wider text-gray-400 uppercase mb-1 transition-all">AI Created</span>
              <span className="text-xl @[17.5rem]:text-2xl font-bold text-white tracking-tight transition-all">14,914</span>
            </div>
          </div>
        </GlassCard>

        <GlassCard padding="md" className="flex items-center gap-5 group @container">
          <div className="w-12 h-12 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shrink-0 group-hover:bg-emerald-500/20 transition-colors">
            <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
          </div>
          <div className="flex-1">
            <div className="flex flex-col">
              <span className="text-[10px] @[17.5rem]:text-[11px] font-semibold tracking-wider text-gray-400 uppercase mb-1 transition-all">Total Published</span>
              <span className="text-xl @[17.5rem]:text-2xl font-bold text-white tracking-tight transition-all">111</span>
            </div>
          </div>
        </GlassCard>

        <GlassCard padding="md" className="flex items-center gap-5 group @container">
          <div className="w-12 h-12 rounded-full bg-rose-500/10 border border-rose-500/20 flex items-center justify-center shrink-0 group-hover:bg-rose-500/20 transition-colors">
            <svg className="w-5 h-5 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          </div>
          <div className="flex-1">
            <div className="flex flex-col">
              <span className="text-[10px] @[17.5rem]:text-[11px] font-semibold tracking-wider text-gray-400 uppercase mb-1 transition-all">Publish Rate (C01)</span>
              <span className="text-xl @[17.5rem]:text-2xl font-bold text-rose-400 tracking-tight transition-all">{PUBLISH_RATE}%</span>
              <span className="text-[10px] text-gray-500 mt-1">{PUBLISH_GAP.toLocaleString()} videos unpublished</span>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Main Funnel Visualization */}
      <ChartCard title="Publishing Pipeline Funnel" subtitle="Uploaded → AI Created → Published (C01)">
        <FunnelChart data={funnelData} />
      </ChartCard>

      {/* Bottom Row: Output Type + Channel Publish Rates */}
      <div className="grid lg:grid-cols-2 gap-10 h-[400px]">
        {/* Publish Rate by Output Type */}
        <ChartCard title="Publish Rate by Output Type" subtitle="Which AI formats convert best? (B01/C01)">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={outputRateData} layout="vertical" margin={{ top: 20, right: 30, left: 10, bottom: 20 }} barSize={28}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" tick={{ fill: '#9ca3af', fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v}%`} />
              <YAxis dataKey="name" type="category" tick={{ fill: '#d1d5db', fontSize: 13, fontWeight: 500 }} axisLine={false} tickLine={false} width={120} />
              <Tooltip
                contentStyle={{ background: 'rgba(9,9,11,0.95)', backdropFilter: 'blur(16px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px', fontWeight: 500 }}
                formatter={(v: any) => [`${v}%`, 'Publish Rate']}
              />
              <Bar dataKey="rate" fill="#ff4756" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Channel Publish Rate */}
        <ChartCard title="Channel Publish Rate" subtitle="Top 10 channels by AI output volume">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={channelRateData} margin={{ top: 20, right: 20, left: 0, bottom: 45 }} barSize={32}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12, fontWeight: 500 }} axisLine={false} tickLine={false} tickMargin={10} interval={0} />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 12, fontWeight: 500 }} axisLine={false} tickLine={false} dx={-10} width={40} tickFormatter={(v) => `${v}%`} />
              <Tooltip
                contentStyle={{ background: 'rgba(9,9,11,0.95)', backdropFilter: 'blur(16px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px', fontWeight: 500 }}
                formatter={(v: any, _: any, entry: any) => [`${v}% (${entry.payload.published} of ${entry.payload.created})`, 'Publish Rate']}
              />
              <Bar dataKey="rate" fill="#ff4756" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
};
