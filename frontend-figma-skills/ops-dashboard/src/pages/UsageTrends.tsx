import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, LineChart, Line, Legend } from 'recharts';
import { useDashboardData } from '../context/DashboardContext';
import { ChartCard } from '../components/ChartCard';
import { GlassCard } from '../components/GlassCard';

export const UsageTrends: React.FC = () => {
  const { monthlyData } = useDashboardData();

  // Monthly data for grouped bar chart
  const barData = monthlyData.map(d => ({
    month: d.month,
    uploaded: d.uploaded,
    created: d.created,
    published: d.published,
  }));

  // MoM Growth Rate line chart data (A03)
  const growthData = monthlyData.filter(d => d.growthRate !== undefined).map(d => ({
    month: d.month,
    growth: d.growthRate!,
  }));

  // Duration data (A02)
  const durationData = monthlyData.map(d => ({
    month: d.month,
    uploadedHrs: Number(d.uploadedDuration) || 0,
    createdHrs: Number(d.createdDuration) || 0,
  }));

  // Computed summary KPIs
  const totalUploaded = monthlyData.reduce((s, d) => s + Number(d.uploaded), 0);
  const totalCreated = monthlyData.reduce((s, d) => s + Number(d.created), 0);
  const totalDurationHrs = monthlyData.reduce((s, d) => s + (Number(d.createdDuration) || 0), 0);
  const peakMonth = monthlyData.reduce((max, d) => d.uploaded > max.uploaded ? d : max, monthlyData[0]);
  const janGrowth = monthlyData.find(d => d.month === 'Jan 26')?.growthRate || 0;

  return (
    <div className="flex flex-col gap-10 pb-12 page-enter">

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <GlassCard padding="lg" interactive className="@container">
          <span className="text-[10px] @[17.5rem]:text-[11px] font-semibold tracking-wider text-gray-400 uppercase mb-1 block">Total Uploads (12 mo)</span>
          <span className="text-2xl font-bold text-white">{totalUploaded.toLocaleString()}</span>
        </GlassCard>
        <GlassCard padding="lg" interactive className="@container">
          <span className="text-[10px] @[17.5rem]:text-[11px] font-semibold tracking-wider text-gray-400 uppercase mb-1 block">Total AI Created</span>
          <span className="text-2xl font-bold text-white">{totalCreated.toLocaleString()}</span>
        </GlassCard>
        <GlassCard padding="lg" interactive className="@container">
          <span className="text-[10px] @[17.5rem]:text-[11px] font-semibold tracking-wider text-gray-400 uppercase mb-1 block">Hours Processed</span>
          <span className="text-2xl font-bold text-white">{totalDurationHrs.toFixed(0)}<span className="text-sm text-gray-400 ml-1">hrs</span></span>
        </GlassCard>
        <GlassCard padding="lg" interactive className="@container">
          <span className="text-[10px] @[17.5rem]:text-[11px] font-semibold tracking-wider text-gray-400 uppercase mb-1 block">Peak Month</span>
          <span className="text-2xl font-bold text-[#ff4756]">{peakMonth.month}</span>
          <span className="text-xs text-gray-500 ml-2">{peakMonth.uploaded} uploads</span>
        </GlassCard>
      </div>

      {/* Monthly Uploaded vs Created vs Published (A01) */}
      <div className="h-[420px]">
        <ChartCard title="Monthly Upload Volume Trend" subtitle="Uploaded · Created · Published (A01)" badge="A01">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData} margin={{ top: 20, right: 20, left: 0, bottom: 45 }} barGap={4}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{ fill: '#9ca3af', fontSize: 11, fontWeight: 500 }} axisLine={false} tickLine={false} dy={16} />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 12, fontWeight: 500 }} axisLine={false} tickLine={false} dx={-10} width={50} />
              <Tooltip
                contentStyle={{ background: 'rgba(9,9,11,0.95)', backdropFilter: 'blur(16px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px', fontWeight: 500 }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px', fontSize: '12px', fontWeight: 500 }} />
              <Bar dataKey="uploaded" fill="#ff4756" radius={[4, 4, 0, 0]} name="Uploaded" />
              <Bar dataKey="created" fill="#ff6d78" radius={[4, 4, 0, 0]} name="AI Created" opacity={0.7} />
              <Bar dataKey="published" fill="#34d399" radius={[4, 4, 0, 0]} name="Published" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Bottom Row: Growth Rate + Duration */}
      <div className="grid lg:grid-cols-2 gap-10 h-[380px]">
        {/* MoM Growth Rate (A03) */}
        <ChartCard title="Month-over-Month Growth" subtitle={`Upload volume growth rate (A03) · Jan growth: ${janGrowth > 0 ? '+' : ''}${janGrowth}%`}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={growthData} margin={{ top: 20, right: 20, left: 0, bottom: 30 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{ fill: '#9ca3af', fontSize: 11, fontWeight: 500 }} axisLine={false} tickLine={false} dy={16} />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 12, fontWeight: 500 }} axisLine={false} tickLine={false} dx={-10} width={50} tickFormatter={(v) => `${v}%`} />
              <Tooltip
                contentStyle={{ background: 'rgba(9,9,11,0.95)', backdropFilter: 'blur(16px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px', fontWeight: 500 }}
                formatter={(v: any) => [`${v > 0 ? '+' : ''}${v}%`, 'MoM Growth']}
              />
              <Line type="monotone" dataKey="growth" stroke="#ff4756" strokeWidth={3} dot={{ fill: '#000', stroke: '#ff4756', strokeWidth: 2, r: 4 }} activeDot={{ r: 7, fill: '#ff4756' }} />
              {/* Zero reference line */}
              <CartesianGrid horizontalPoints={[0]} stroke="rgba(255,255,255,0.15)" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Duration Processed (A02) */}
        <ChartCard title="Duration Processed" subtitle="Hours of content processed per month (A02)">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={durationData} margin={{ top: 20, right: 20, left: 0, bottom: 45 }} barGap={4}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{ fill: '#9ca3af', fontSize: 11, fontWeight: 500 }} axisLine={false} tickLine={false} dy={16} />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 12, fontWeight: 500 }} axisLine={false} tickLine={false} dx={-10} width={50} tickFormatter={(v) => `${v}h`} />
              <Tooltip
                contentStyle={{ background: 'rgba(9,9,11,0.95)', backdropFilter: 'blur(16px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px', fontWeight: 500 }}
                formatter={(v: any) => [`${Number(v).toFixed(1)} hrs`]}
              />
              <Legend wrapperStyle={{ paddingTop: '20px', fontSize: '12px', fontWeight: 500 }} />
              <Bar dataKey="uploadedHrs" fill="#ff4756" radius={[4, 4, 0, 0]} name="Uploaded Duration" />
              <Bar dataKey="createdHrs" fill="#ff6d78" radius={[4, 4, 0, 0]} name="Created Duration" opacity={0.7} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
};
