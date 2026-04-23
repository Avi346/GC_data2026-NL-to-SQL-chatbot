import type {
    KPIMetric, MonthlyDataPoint, ChannelData, UserData,
    PlatformPublishData, MixDataPoint, FunnelStep, BenchmarkKPI,
    ScatterPoint, InsightCard, LanguageData, InputTypeData, OutputTypeData, ChatMessage
} from '../types';

// ============================================================
// RAW DATA FROM CSVs — All values sourced from real CLIENT_1 data
// ============================================================

// --- monthly-chart.csv (sorted chronologically) ---
export const monthlyData: MonthlyDataPoint[] = [
    { month: 'Mar 25', uploaded: 639, created: 2555, published: 0 },
    { month: 'Apr 25', uploaded: 533, created: 1656, published: 44 },
    { month: 'May 25', uploaded: 217, created: 642, published: 4 },
    { month: 'Jun 25', uploaded: 239, created: 907, published: 3 },
    { month: 'Jul 25', uploaded: 284, created: 892, published: 0 },
    { month: 'Aug 25', uploaded: 256, created: 699, published: 7 },
    { month: 'Sep 25', uploaded: 227, created: 684, published: 0 },
    { month: 'Oct 25', uploaded: 343, created: 1046, published: 10 },
    { month: 'Nov 25', uploaded: 353, created: 943, published: 2 },
    { month: 'Dec 25', uploaded: 194, created: 644, published: 7 },
    { month: 'Jan 26', uploaded: 492, created: 1492, published: 20 },
    { month: 'Feb 26', uploaded: 676, created: 2756, published: 14 },
];

// Compute MoM growth rates
monthlyData.forEach((d, i) => {
    if (i > 0) {
        const prev = monthlyData[i - 1].uploaded;
        d.growthRate = prev > 0 ? parseFloat((((d.uploaded - prev) / prev) * 100).toFixed(1)) : 0;
    }
});

// --- month-wise-duration.csv (hours, sorted chronologically) ---
const durationMap: Record<string, { up: number; cr: number; pub: number }> = {
    'Mar 25': { up: 122.06, cr: 176.28, pub: 0 },
    'Apr 25': { up: 65.47, cr: 98.02, pub: 1.10 },
    'May 25': { up: 46.95, cr: 64.45, pub: 0.06 },
    'Jun 25': { up: 47.18, cr: 84.16, pub: 0.20 },
    'Jul 25': { up: 33.62, cr: 66.84, pub: 0 },
    'Aug 25': { up: 39.94, cr: 64.52, pub: 0.11 },
    'Sep 25': { up: 34.35, cr: 58.63, pub: 0 },
    'Oct 25': { up: 47.86, cr: 94.29, pub: 0.25 },
    'Nov 25': { up: 48.12, cr: 83.38, pub: 0.04 },
    'Dec 25': { up: 38.26, cr: 71.70, pub: 0.24 },
    'Jan 26': { up: 122.00, cr: 191.46, pub: 1.45 },
    'Feb 26': { up: 161.87, cr: 301.51, pub: 0.94 },
};
monthlyData.forEach(d => {
    const dur = durationMap[d.month];
    if (dur) {
        d.uploadedDuration = dur.up;
        d.createdDuration = dur.cr;
        d.publishedDuration = dur.pub;
    }
});

// --- CLIENT 1 combined_data.csv (channel-level aggregates) ---
export const channelData: ChannelData[] = [
    { name: 'A', uploaded: 1470, created: 4725, published: 71, publishRate: 1.50, uploadedDuration: '227:24:21', createdDuration: '410:36:38', publishedDuration: '3:02:30' },
    { name: 'B', uploaded: 1293, created: 4251, published: 19, publishRate: 0.45, uploadedDuration: '297:15:05', createdDuration: '472:02:39', publishedDuration: '0:24:19' },
    { name: 'C', uploaded: 765, created: 2631, published: 14, publishRate: 0.53, uploadedDuration: '158:25:12', createdDuration: '235:03:49', publishedDuration: '0:27:44' },
    { name: 'D', uploaded: 221, created: 701, published: 0, publishRate: 0, uploadedDuration: '23:31:11', createdDuration: '42:08:02', publishedDuration: '0:00:00' },
    { name: 'E', uploaded: 201, created: 807, published: 5, publishRate: 0.62, uploadedDuration: '25:34:42', createdDuration: '59:03:55', publishedDuration: '0:16:07' },
    { name: 'F', uploaded: 130, created: 320, published: 0, publishRate: 0, uploadedDuration: '17:35:35', createdDuration: '25:23:17', publishedDuration: '0:00:00' },
    { name: 'G', uploaded: 106, created: 351, published: 1, publishRate: 0.28, uploadedDuration: '17:42:41', createdDuration: '33:33:50', publishedDuration: '0:03:01' },
    { name: 'H', uploaded: 89, created: 329, published: 1, publishRate: 0.30, uploadedDuration: '10:17:01', createdDuration: '20:33:19', publishedDuration: '0:08:56' },
    { name: 'I', uploaded: 59, created: 262, published: 0, publishRate: 0, uploadedDuration: '10:56:20', createdDuration: '22:41:30', publishedDuration: '0:00:00' },
    { name: 'J', uploaded: 37, created: 145, published: 0, publishRate: 0, uploadedDuration: '5:39:49', createdDuration: '11:11:49', publishedDuration: '0:00:00' },
    { name: 'K', uploaded: 29, created: 83, published: 0, publishRate: 0, uploadedDuration: '2:42:05', createdDuration: '4:30:33', publishedDuration: '0:00:00' },
    { name: 'L', uploaded: 17, created: 216, published: 0, publishRate: 0, uploadedDuration: '8:05:43', createdDuration: '13:59:58', publishedDuration: '0:00:00' },
    { name: 'M', uploaded: 8, created: 14, published: 0, publishRate: 0, uploadedDuration: '0:35:20', createdDuration: '0:57:33', publishedDuration: '0:00:00' },
    { name: 'N', uploaded: 8, created: 21, published: 0, publishRate: 0, uploadedDuration: '0:27:48', createdDuration: '0:41:05', publishedDuration: '0:00:00' },
    { name: 'O', uploaded: 7, created: 18, published: 0, publishRate: 0, uploadedDuration: '0:17:58', createdDuration: '0:39:48', publishedDuration: '0:00:00' },
    { name: 'P', uploaded: 5, created: 14, published: 0, publishRate: 0, uploadedDuration: '0:35:56', createdDuration: '0:50:05', publishedDuration: '0:00:00' },
    { name: 'Q', uploaded: 5, created: 19, published: 0, publishRate: 0, uploadedDuration: '0:22:05', createdDuration: '0:55:32', publishedDuration: '0:00:00' },
    { name: 'R', uploaded: 3, created: 7, published: 0, publishRate: 0, uploadedDuration: '0:11:14', createdDuration: '0:16:33', publishedDuration: '0:00:00' },
];

// --- combined_data by user.csv (top users) ---
export const userData: UserData[] = [
    { name: 'Chandan', uploaded: 489, created: 2152, published: 19, publishRate: 0.88, uploadedDuration: '100:43:58', createdDuration: '209:18:47', publishedDuration: '01:13:40' },
    { name: 'QA-Purushottam', uploaded: 309, created: 1227, published: 13, publishRate: 1.06, uploadedDuration: '33:08:48', createdDuration: '55:19:21', publishedDuration: '00:21:34' },
    { name: 'vikas.s@moolya.com', uploaded: 265, created: 1094, published: 4, publishRate: 0.37, uploadedDuration: '61:22:20', createdDuration: '101:55:47', publishedDuration: '00:15:23' },
    { name: 'Sandeep Belaki', uploaded: 253, created: 1039, published: 7, publishRate: 0.67, uploadedDuration: '39:59:44', createdDuration: '84:32:25', publishedDuration: '00:08:12' },
    { name: 'Nitesh', uploaded: 224, created: 959, published: 0, publishRate: 0, uploadedDuration: '59:57:41', createdDuration: '87:54:11', publishedDuration: '00:00:00' },
    { name: 'Abhishek', uploaded: 201, created: 408, published: 8, publishRate: 1.96, uploadedDuration: '19:25:46', createdDuration: '26:56:37', publishedDuration: '00:25:04' },
    { name: 'Auto Upload', uploaded: 185, created: 220, published: 0, publishRate: 0, uploadedDuration: '41:52:06', createdDuration: '42:52:30', publishedDuration: '00:00:00' },
    { name: 'Subhesh', uploaded: 184, created: 489, published: 7, publishRate: 1.43, uploadedDuration: '21:36:47', createdDuration: '30:19:43', publishedDuration: '00:13:00' },
    { name: 'Trivendra', uploaded: 179, created: 825, published: 3, publishRate: 0.36, uploadedDuration: '61:09:11', createdDuration: '111:06:20', publishedDuration: '00:10:00' },
    { name: 'Dheeraj Pareek', uploaded: 166, created: 482, published: 2, publishRate: 0.41, uploadedDuration: '16:07:52', createdDuration: '32:23:39', publishedDuration: '00:02:13' },
    { name: 'vinay singh', uploaded: 161, created: 530, published: 3, publishRate: 0.57, uploadedDuration: '33:30:02', createdDuration: '44:37:01', publishedDuration: '00:03:08' },
    { name: 'Neha', uploaded: 158, created: 510, published: 10, publishRate: 1.96, uploadedDuration: '20:11:39', createdDuration: '44:32:26', publishedDuration: '00:31:14' },
    { name: 'Subhash (moolya)', uploaded: 154, created: 457, published: 0, publishRate: 0, uploadedDuration: '14:29:47', createdDuration: '30:55:10', publishedDuration: '00:00:00' },
    { name: 'Adarsh', uploaded: 141, created: 262, published: 5, publishRate: 1.91, uploadedDuration: '17:37:54', createdDuration: '24:54:18', publishedDuration: '00:25:52' },
    { name: 'Anamika Singh', uploaded: 121, created: 567, published: 2, publishRate: 0.35, uploadedDuration: '30:51:09', createdDuration: '65:22:15', publishedDuration: '00:04:32' },
    { name: 'AB', uploaded: 101, created: 368, published: 0, publishRate: 0, uploadedDuration: '27:58:37', createdDuration: '42:08:26', publishedDuration: '00:00:00' },
    { name: 'Divyanshu Dutta Roy', uploaded: 95, created: 380, published: 0, publishRate: 0, uploadedDuration: '32:58:37', createdDuration: '47:30:31', publishedDuration: '00:00:00' },
    { name: 'Vaibhav', uploaded: 94, created: 268, published: 0, publishRate: 0, uploadedDuration: '26:54:03', createdDuration: '38:06:50', publishedDuration: '00:00:00' },
    { name: 'Alok Rai', uploaded: 86, created: 143, published: 4, publishRate: 2.80, uploadedDuration: '05:07:43', createdDuration: '06:31:45', publishedDuration: '00:02:42' },
    { name: 'sukhleen', uploaded: 84, created: 221, published: 1, publishRate: 0.45, uploadedDuration: '13:30:24', createdDuration: '21:14:09', publishedDuration: '00:01:12' },
];

// --- combined_data by input type.csv ---
export const inputTypeData: InputTypeData[] = [
    { name: 'Interview', uploaded: 1299, created: 4972, published: 35, publishAffinity: 0.70 },
    { name: 'News Bulletin', uploaded: 1026, created: 3238, published: 39, publishAffinity: 1.20 },
    { name: 'Special Reports', uploaded: 755, created: 2129, published: 15, publishAffinity: 0.70 },
    { name: 'Speech', uploaded: 742, created: 2390, published: 12, publishAffinity: 0.50 },
    { name: 'Debate', uploaded: 290, created: 1074, published: 5, publishAffinity: 0.47 },
    { name: 'Press Conference', uploaded: 280, created: 973, published: 2, publishAffinity: 0.21 },
    { name: 'Discussion Show', uploaded: 19, created: 79, published: 3, publishAffinity: 3.80 },
    { name: 'Sports Show', uploaded: 17, created: 19, published: 0, publishAffinity: 0 },
    { name: 'Unknown', uploaded: 12, created: 12, published: 0, publishAffinity: 0 },
    { name: 'Podcast', uploaded: 8, created: 21, published: 0, publishAffinity: 0 },
    { name: 'Drama', uploaded: 4, created: 4, published: 0, publishAffinity: 0 },
    { name: 'In-Brief', uploaded: 1, created: 3, published: 0, publishAffinity: 0 },
];

// --- combined_data by output type.csv ---
export const outputTypeData: OutputTypeData[] = [
    { name: 'Full Package', uploaded: 4453, created: 4453, published: 35, publishRate: 0.79 },
    { name: 'Key Moments', uploaded: 0, created: 6377, published: 41, publishRate: 0.64 },
    { name: 'Chapters', uploaded: 0, created: 2007, published: 2, publishRate: 0.10 },
    { name: 'My Key Moments', uploaded: 0, created: 1237, published: 32, publishRate: 2.59 },
    { name: 'Summary', uploaded: 0, created: 840, published: 1, publishRate: 0.12 },
];

// --- combined_data by language.csv ---
export const languageData: LanguageData[] = [
    { language: 'English (en)', uploaded: 2647, created: 8861, published: 91, publishRate: 1.03 },
    { language: 'Hindi (hi)', uploaded: 1792, created: 6021, published: 20, publishRate: 0.33 },
    { language: 'Mixed', uploaded: 11, created: 29, published: 0, publishRate: 0 },
    { language: 'Spanish (es)', uploaded: 1, created: 1, published: 0, publishRate: 0 },
    { language: 'Arabic (ar)', uploaded: 1, created: 1, published: 0, publishRate: 0 },
    { language: 'Marathi (mr)', uploaded: 1, created: 1, published: 0, publishRate: 0 },
];

// --- channel-wise-publishing.csv ---
export const platformPublishData: PlatformPublishData[] = [
    { channel: 'A', facebook: 1, instagram: 7, linkedin: 0, reels: 5, shorts: 1, x: 0, youtube: 5, threads: 0, total: 19 },
    { channel: 'B', facebook: 0, instagram: 0, linkedin: 0, reels: 0, shorts: 0, x: 0, youtube: 0, threads: 0, total: 0 },
    { channel: 'C', facebook: 0, instagram: 0, linkedin: 0, reels: 0, shorts: 0, x: 0, youtube: 0, threads: 0, total: 0 },
    { channel: 'D', facebook: 6, instagram: 3, linkedin: 0, reels: 15, shorts: 18, x: 0, youtube: 29, threads: 0, total: 71 },
    { channel: 'E', facebook: 0, instagram: 0, linkedin: 0, reels: 0, shorts: 0, x: 0, youtube: 0, threads: 0, total: 0 },
    { channel: 'F', facebook: 0, instagram: 0, linkedin: 0, reels: 0, shorts: 0, x: 0, youtube: 0, threads: 0, total: 0 },
    { channel: 'G', facebook: 1, instagram: 0, linkedin: 0, reels: 11, shorts: 2, x: 0, youtube: 0, threads: 0, total: 14 },
    { channel: 'H', facebook: 0, instagram: 0, linkedin: 0, reels: 0, shorts: 0, x: 0, youtube: 0, threads: 0, total: 0 },
    { channel: 'I', facebook: 1, instagram: 1, linkedin: 0, reels: 1, shorts: 2, x: 0, youtube: 0, threads: 0, total: 5 },
    { channel: 'J', facebook: 0, instagram: 0, linkedin: 0, reels: 0, shorts: 0, x: 0, youtube: 0, threads: 0, total: 0 },
    { channel: 'K', facebook: 0, instagram: 0, linkedin: 0, reels: 0, shorts: 0, x: 0, youtube: 0, threads: 0, total: 0 },
    { channel: 'L', facebook: 0, instagram: 0, linkedin: 0, reels: 0, shorts: 0, x: 0, youtube: 0, threads: 0, total: 0 },
    { channel: 'M', facebook: 0, instagram: 0, linkedin: 0, reels: 0, shorts: 0, x: 0, youtube: 0, threads: 0, total: 0 },
    { channel: 'N', facebook: 0, instagram: 0, linkedin: 0, reels: 0, shorts: 0, x: 0, youtube: 0, threads: 0, total: 0 },
    { channel: 'O', facebook: 0, instagram: 0, linkedin: 0, reels: 0, shorts: 0, x: 0, youtube: 0, threads: 0, total: 0 },
    { channel: 'P', facebook: 0, instagram: 0, linkedin: 0, reels: 1, shorts: 0, x: 0, youtube: 0, threads: 0, total: 1 },
    { channel: 'Q', facebook: 0, instagram: 0, linkedin: 0, reels: 0, shorts: 0, x: 0, youtube: 1, threads: 0, total: 1 },
    { channel: 'R', facebook: 0, instagram: 0, linkedin: 0, reels: 0, shorts: 0, x: 0, youtube: 0, threads: 0, total: 0 },
];

// ============================================================
// COMPUTED KPIs
// ============================================================

const TOTAL_UPLOADED = 4453;
const TOTAL_CREATED = 14914;
const TOTAL_PUBLISHED = 111;
const TOTAL_CHANNELS = 18;
const CHANNELS_WITH_UPLOADS = 18; // all 18 have uploads > 0
const ZERO_PUBLISHER_CHANNELS = channelData.filter(c => c.published === 0).length; // 12

// Platform totals from channel-wise-publishing
const platformTotals = {
    youtube: 35, reels: 32, shorts: 23, facebook: 9, instagram: 11, linkedin: 0, x: 0, threads: 0,
};

// Ghost user calculation: users with published = 0 out of total users
const TOTAL_USERS = userData.length + 25; // ~45 total from CSV
const GHOST_USERS = 30; // 30 of 45 users have published = 0

// --- A: Usage & Adoption ---
export const PUBLISH_RATE = parseFloat(((TOTAL_PUBLISHED / TOTAL_CREATED) * 100).toFixed(2)); // 0.74%
export const PUBLISH_GAP = TOTAL_CREATED - TOTAL_PUBLISHED; // 14,803
export const CHANNEL_ACTIVATION_RATE = parseFloat(((CHANNELS_WITH_UPLOADS / TOTAL_CHANNELS) * 100).toFixed(1)); // 100%
export const ZERO_PUBLISHER_RATE = parseFloat(((ZERO_PUBLISHER_CHANNELS / TOTAL_CHANNELS) * 100).toFixed(1)); // 66.7%
export const GHOST_USER_RATE = parseFloat(((GHOST_USERS / TOTAL_USERS) * 100).toFixed(1)); // ~66.7%

// --- Executive KPI Cards ---
export const kpiMetrics: KPIMetric[] = [
    { id: 'publish-rate', label: 'Publish Rate', value: `${PUBLISH_RATE}%`, status: 'critical', trend: 'down', delta: -0.12 },
    { id: 'total-uploaded', label: 'Total Uploaded', value: TOTAL_UPLOADED.toLocaleString(), trend: 'up', delta: 37.4 },
    { id: 'total-created', label: 'Total AI Created', value: TOTAL_CREATED.toLocaleString(), trend: 'up', delta: 84.7 },
    { id: 'total-published', label: 'Total Published', value: TOTAL_PUBLISHED.toLocaleString(), trend: 'down', delta: -30.0 },
    { id: 'publish-gap', label: 'Unpublished Gap', value: PUBLISH_GAP.toLocaleString(), status: 'critical', trend: 'up', delta: 4.5 },
    { id: 'zero-pub-rate', label: 'Zero-Publisher Channels', value: `${ZERO_PUBLISHER_RATE}%`, status: 'critical', trend: 'neutral', delta: 0 },
    { id: 'ghost-users', label: 'Ghost User Rate', value: `${GHOST_USER_RATE}%`, status: 'concerning', trend: 'neutral', delta: 0 },
    { id: 'channel-activation', label: 'Channel Activation', value: `${CHANNEL_ACTIVATION_RATE}%`, status: 'healthy', trend: 'neutral', delta: 0 },
];

// --- Input Mix (for donut charts, top 5 by created count) ---
export const inputMixData: MixDataPoint[] = [
    { name: 'Interview', value: 4972, color: '#ff4756', publishRate: 0.70 },
    { name: 'News Bulletin', value: 3238, color: '#ff6d78', publishRate: 1.20 },
    { name: 'Speech', value: 2390, color: '#ff8a94', publishRate: 0.50 },
    { name: 'Special Reports', value: 2129, color: '#ffb7bc', publishRate: 0.70 },
    { name: 'Debate', value: 1074, color: '#ffd1d4', publishRate: 0.47 },
];

// --- Output Mix (for donut charts) ---
export const outputMixData: MixDataPoint[] = [
    { name: 'Key Moments', value: 6377, color: '#ff4756', publishRate: 0.64 },
    { name: 'Full Package', value: 4453, color: '#ff6d78', publishRate: 0.79 },
    { name: 'Chapters', value: 2007, color: '#ff8a94', publishRate: 0.10 },
    { name: 'My Key Moments', value: 1237, color: '#ffb7bc', publishRate: 2.59 },
    { name: 'Summary', value: 840, color: '#ffd1d4', publishRate: 0.12 },
];

// --- Funnel Data ---
export const funnelData: FunnelStep[] = [
    { id: 'uploaded', label: 'Raw Videos Uploaded', value: TOTAL_UPLOADED, color: '#ff4756' },
    { id: 'created', label: 'AI Videos Created', value: TOTAL_CREATED, color: '#ff6d78' },
    { id: 'published', label: 'Successfully Published', value: TOTAL_PUBLISHED, color: '#34d399' },
];

// --- Platform Share (D04) ---
export const platformShareData: MixDataPoint[] = [
    { name: 'YouTube', value: platformTotals.youtube, color: '#ff4756' },
    { name: 'Reels', value: platformTotals.reels, color: '#ff6d78' },
    { name: 'Shorts', value: platformTotals.shorts, color: '#ff8a94' },
    { name: 'Instagram', value: platformTotals.instagram, color: '#ffb7bc' },
    { name: 'Facebook', value: platformTotals.facebook, color: '#ffd1d4' },
];

// --- Scatter Data (X02 - Volume vs Publish Output) ---
export const scatterData: ScatterPoint[] = channelData.map(ch => ({
    name: `Channel ${ch.name}`,
    x: ch.created,
    y: ch.published,
    z: Math.sqrt(ch.uploaded) * 8,
    publishRate: ch.publishRate,
    color: ch.publishRate >= 1 ? '#34d399' : ch.publishRate > 0 ? '#fbbf24' : '#f43f5e',
}));

// --- Benchmark KPIs ---
export const benchmarkKPIs: BenchmarkKPI[] = [
    {
        id: 'publish-rate', label: 'Publish Rate (C01)', value: PUBLISH_RATE, displayValue: `${PUBLISH_RATE}%`,
        status: 'critical',
        thresholds: { healthy: '> 5%', concerning: '1–5%', critical: '< 1%' },
        insight: 'Less than 1 in 135 AI-generated videos is ever published. The platform is generating enormous AI value that never reaches an audience.'
    },
    {
        id: 'ghost-user', label: 'Ghost User Rate (C03)', value: GHOST_USER_RATE, displayValue: `${GHOST_USER_RATE}%`,
        status: 'concerning',
        thresholds: { healthy: '< 30%', concerning: '30–70%', critical: '> 70%' },
        insight: 'Two-thirds of users have never published a single video despite uploading content to the platform.'
    },
    {
        id: 'zero-pub-channel', label: 'Zero-Publisher Channels (C04)', value: ZERO_PUBLISHER_RATE, displayValue: `${ZERO_PUBLISHER_RATE}%`,
        status: 'critical',
        thresholds: { healthy: '< 20%', concerning: '20–50%', critical: '> 50%' },
        insight: 'Two-thirds of channels have never published — a fundamental platform value-delivery problem and renewal risk.'
    },
    {
        id: 'top-contributor', label: 'Top Contributor Index (D01)', value: 16.8, displayValue: '16.8%',
        status: 'healthy',
        thresholds: { healthy: '< 30%', concerning: '30–50%', critical: '> 50%' },
        insight: 'Channel A has the most distributed team (16.8%). However, several smaller channels exceed 50%, indicating key-person risk.'
    },
    {
        id: 'user-concentration', label: 'User Concentration (D02)', value: 16.8, displayValue: '16.8%',
        status: 'healthy',
        thresholds: { healthy: '< 25%', concerning: '25–50%', critical: '> 50%' },
        insight: 'Channel A is well distributed. Contrast with Channel O at 85.7% — extreme single-point-of-failure risk.'
    },
    {
        id: 'channel-share', label: 'Channel Share (X01)', value: 64.0, displayValue: '64.0%',
        status: 'critical',
        thresholds: { healthy: '< 40%', concerning: '40–60%', critical: '> 60%' },
        insight: 'Channel A commands 64% of all published output. A single disruption could collapse two-thirds of publishing overnight.'
    },
    {
        id: 'platform-speciality', label: 'Platform Speciality (D05)', value: 40.9, displayValue: '40.9%',
        status: 'concerning',
        thresholds: { healthy: '< 40%', concerning: '40–70%', critical: '> 70%' },
        insight: 'Channel D is a YouTube specialist at 40.9%. Channel G is Reels-first at 78.6%. Tailor AI output formats per channel.'
    },
];

// --- KPI-Driven Insights ---
export const insightsData: InsightCard[] = [
    {
        id: '1', title: 'My Key Moments: Conversion Champion', type: 'positive',
        description: 'My Key Moments has a 2.59% publish rate — 4× better than Key Moments (0.64%). Rebalancing AI output toward this format is the fastest lever for improving overall publish rate.',
        metric: 'Publish Rate', metricValue: '2.59%'
    },
    {
        id: '2', title: 'Key Moments: Waste in Progress', type: 'negative',
        description: 'Key Moments dominates output at 42.8% share but has only a 0.64% publish rate. The client is generating the wrong output type at scale.',
        metric: 'Output Share', metricValue: '42.8%'
    },
    {
        id: '3', title: 'English vs Hindi Publishing Gap', type: 'negative',
        description: 'English content publishes at 3× the rate of Hindi (1.03% vs 0.33%). Improving Hindi publish rate to even 0.70% would double Hindi publishing output.',
        metric: 'Hindi Rate', metricValue: '0.33%'
    },
    {
        id: '4', title: 'Channel A Concentration Risk', type: 'negative',
        description: 'Channel A commands 64% of all published output. Top 3 channels account for 93.7%. A single disruption could collapse publishing overnight.',
        metric: 'Channel A Share', metricValue: '64.0%'
    },
    {
        id: '5', title: 'Discussion Show: Hidden Gem', type: 'positive',
        description: 'Despite being a small category (79 created), Discussion Show has the highest publish affinity at 3.80% — investigate what makes these clips publication-ready.',
        metric: 'Affinity', metricValue: '3.80%'
    },
    {
        id: '6', title: 'Feb 2026: Record Upload Month', type: 'positive',
        description: '676 uploads in February 2026 — the highest single month on record. After dipping mid-year (Jul: 284), uploads rebounded strongly in Jan–Feb 2026.',
        metric: 'Uploads', metricValue: '676'
    },
];

// --- Chat History ---
export const chatHistory: ChatMessage[] = [
    { id: '1', role: 'user', content: 'Why is our publish rate so low?', timestamp: '10:42 AM' },
    { id: '2', role: 'assistant', content: 'The overall publish rate is 0.74% — less than 1 in 135 AI-generated videos is published. The primary bottleneck is that 12 of 18 channels (66.7%) have never published a single video. Focus CS intervention on these zero-publisher channels, particularly Channel D which has 701 AI outputs but zero publications.', timestamp: '10:42 AM' },
];
