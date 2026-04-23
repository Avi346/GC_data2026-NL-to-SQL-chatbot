# Operations Dashboard - AI Media Publishing Pipeline

![Dashboard Overview](public/vite.svg) *(Replace with actual dashboard screenshot)*

A robust, premium, high-performance monitoring dashboard tailored for tracking AI media processing and publishing pipelines. Engineered with a "Liquid Glass" aesthetic, real-time visual feedback, and an integrated brand identity. 

This dashboard visualizes real client data surrounding usage, adoption rates, platform analytics, data quality, and ROI metrics for AI-generated media content.

---

## 🚀 Quick Start

To run this project locally, ensure you have [Node.js](https://nodejs.org/) (v18+) installed.

```bash
# 1. Clone the repository and navigate to the dashboard folder
cd ops-dashboard

# 2. Install dependencies
npm install

# 3. Start the Vite development server
npm run dev

# 4. Build for production
npm run build
```

The application will be served locally at `http://localhost:5173`.

---

## ✨ Key Features & Views

The dashboard is composed of several fully-responsive data views tailored to operations and analytics:

1. **Executive Summary**
   - High-level KPI index (Publish Rate, Channel Activation, Unused Content Gap).
   - Monthly progression graphs and trend deltas.
   
2. **Usage & Adoption**
   - User engagement scatter plots.
   - Channel vs. active creator analysis.
   - Top contributor matrices.

3. **Publishing Funnel**
   - Step-by-step funnel visualization (`Uploaded` → `AI Created` → `Successfully Published`).
   - Conversion rate analytics by format (e.g., Short Form, Key Moments, Full Package).
   - Channel-wise publish performance.

4. **Data Quality & Platform Analytics**
   - Language translation metrics.
   - Cross-platform distribution (YouTube, X, Reels, LinkedIn).
   - Actionable data insights and anomaly detection.

---

## 🏗️ Technical Architecture

This application strictly follows a component-driven architecture, ensuring high reusability and isolated business logic.

### Tech Stack
- **Core**: React 19 + TypeScript
- **Build Tool**: Vite 6 (Lightning fast HMR & optimized production builds)
- **Styling**: Tailwind CSS 4 (Atomic CSS combined with custom design tokens)
- **Data Visualization**: Recharts (Customized with specialized `<Cell>` formatting and responsive containers)
- **Icons / Typography**: Lucide React + custom Montreal Serial font families.

### Folder Structure

```text
src/
├── components/          # Reusable atomic UI elements
│   ├── ChartCard.tsx    # Card container optimized for responsive Recharts
│   ├── FunnelChart.tsx  # Custom pipeline conversion chart
│   └── GlassCard.tsx    # Core structural card with glassmorphism 
├── data/                # Data engines and static assets
│   └── kpiData.ts       # Central data brain, transforming raw metrics into charts
├── layout/              # Core layout structure
│   ├── AppLayout.tsx    # Main app shell (Sidebar container, Navbar)
│   ├── Navbar.tsx       # Top search, auth, and environment context
│   └── Sidebar.tsx      # Main navigation routing panel
├── pages/               # Top-level Page components (Route targets)
│   ├── ExecutiveSummary.tsx
│   ├── PublishingFunnel.tsx
│   └── ...
├── types/               # TypeScript definitions and interfaces
│   └── index.ts         # Shared Data Models (FunnelStep, Metric, etc.)
├── App.tsx              # Main Application router & provider
└── index.css            # Global stylesheet + CSS variables
```

---

## 🎨 Design System: "Liquid Glass"

The UI features a deeply integrated design language crafted for dark modes and high-tech aesthetics:

- **Glassmorphism Base:** Most cards (`<GlassCard />`) use deep blurs (`backdrop-blur-[40px]`), thin 5% white borders, and subtle RGBA gradients to simulate frosted glass against the space-black background.
- **Dynamic Accent Colors:** 
  - **Primary Brand Red**: `#ff4756` (Used for active states, warnings, error states).
  - **Success Emerald**: `#34d399` (Used for positive growth metrics and published completions).
  - **Warning Amber**: `#fbbf24` (Used for neutral trends).
- **Typography Matrix:** 
  - Functional Numbers / Monospace (Tailwind `font-mono`) used for exact metric tracking to ensure tabular numbers align perfectly.
  - Headers / Titles rely on **Montreal Serial** to invoke a strong, cinematic tech brand feel.
- **Micro-Interactions**: Hover states reveal deep glowing shadows and border transitions, managed seamlessly via Tailwind group-hover variants.

---

## 📊 Data Pipeline Explained

The dashboard visualizes real-time metrics by fetching aggregated analytics from a dynamic PostgreSQL backend (`http://localhost:5000/api/dashboard-data`). 

1. **Data Ingestion via UI**: Administrators use the integrated **Data Ingestion** view in the sidebar to upload raw `combined_data...csv` exports.
2. **Backend Processing**: The Express API parses the CSV using `csv-parse` and aggressively upserts the normalized data directly into PostgreSQL tables (`user_data`, `channel_data`, `monthly_data`, etc.).
3. **Dynamic Refresh**: On successful upload, the React frontend context (`DashboardContext`) instantly refetches the data payload, seamlessly piping fresh metrics into the `<ResponsiveContainer>` wrapped Recharts elements without a page reload. 
4. **Computed KPIs**: Instead of hardcoding graph values, `DashboardContext` computes exact relationships on the fly (e.g., `PUBLISH_RATE = (TOTAL_PUBLISHED / TOTAL_CREATED) * 100`).

*(Note: Direct modifications to CSV files on the server disk will not be reflected until uploaded through the Data Ingestion UI, as the dashboard reads strictly from the database.)* 

---

## ⚙️ Available Scripts

In the project directory, you can run:

- `npm run dev` - Runs the app in development mode.
- `npm run build` - Compiles tracking TypeScript checks (`tsc -b`) and bundles the Vite app for production to the `dist` folder.
- `npm run preview` - Locally serve the static production build created by `npm run build`.

---

## 🤝 Contribution Guidelines

When adding new charts or views to the Operations Dashboard:
1. Try to reuse `<ChartCard>` and `<GlassCard>` wrappers to maintain border radii and padding consistency.
2. Keep Recharts implementations responsive. Always wrap charts in an inline `100%` / `100vh`/`h-` constrained `ResponsiveContainer`.
3. Adhere to the defined color palette when rendering `<Bar>` or `<Cell>` elements format.

---
*Maintained by the OS Analytics Team*
