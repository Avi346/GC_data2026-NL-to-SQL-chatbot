// === Core KPI Types ===

export interface KPIMetric {
  id: string;
  label: string;
  value: string | number;
  unit?: string;
  delta?: number;
  trend?: 'up' | 'down' | 'neutral';
  status?: 'healthy' | 'concerning' | 'critical';
}

export interface MonthlyDataPoint {
  month: string;
  uploaded: number;
  created: number;
  published: number;
  uploadedDuration?: number; // hours
  createdDuration?: number;
  publishedDuration?: number;
  growthRate?: number; // MoM %
}

export interface ChannelData {
  name: string;
  uploaded: number;
  created: number;
  published: number;
  publishRate: number;
  uploadedDuration: string;
  createdDuration: string;
  publishedDuration: string;
}

export interface UserData {
  name: string;
  uploaded: number;
  created: number;
  published: number;
  publishRate: number;
  uploadedDuration: string;
  createdDuration: string;
  publishedDuration: string;
}

export interface ChannelUserData {
  channel: string;
  user: string;
  uploaded: number;
  created: number;
  published: number;
}

export interface PlatformPublishData {
  channel: string;
  facebook: number;
  instagram: number;
  linkedin: number;
  reels: number;
  shorts: number;
  x: number;
  youtube: number;
  threads: number;
  total: number;
}

export interface InputTypeData {
  name: string;
  uploaded: number;
  created: number;
  published: number;
  publishAffinity: number;
}

export interface OutputTypeData {
  name: string;
  uploaded: number;
  created: number;
  published: number;
  publishRate: number;
}

export interface LanguageData {
  language: string;
  uploaded: number;
  created: number;
  published: number;
  publishRate: number;
}

export interface MixDataPoint {
  name: string;
  value: number;
  color: string;
  publishRate?: number;
}

export interface FunnelStep {
  id: string;
  label: string;
  value: number;
  color: string;
}

export interface BenchmarkKPI {
  id: string;
  label: string;
  value: number;
  displayValue: string;
  status: 'healthy' | 'concerning' | 'critical';
  thresholds: { healthy: string; concerning: string; critical: string };
  insight: string;
}

export interface ScatterPoint {
  name: string;
  x: number; // Created Count
  y: number; // Published Count
  z: number; // sqrt(Uploaded) for bubble size
  color: string;
  publishRate: number;
}

export interface InsightCard {
  id: string;
  title: string;
  description: string;
  type: 'positive' | 'negative' | 'neutral';
  metric?: string;
  metricValue?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}
