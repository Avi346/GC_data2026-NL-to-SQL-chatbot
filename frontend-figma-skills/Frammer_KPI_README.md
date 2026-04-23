# FRAMMER AI — Analytics Dashboard KPI Reference

> **For the Antigravity Dashboard Engineering Team**  
> Version 1.0 · March 2026  
> Data Source: CLIENT_1 anonymised dataset · 18 channels · 14,918 video records  
> Context: IIT General Championship – Data Analytics 2026 · Industry Case Partner: Frammer AI

---

## Table of Contents

- [Document Overview](#document-overview)
- [Benchmark Quick-Reference](#benchmark-quick-reference)
- [Section A — Usage & Adoption](#section-a--usage--adoption)
  - [A01 · Upload Volume Trend](#a01--upload-volume-trend)
  - [A02 · Total Duration Processed per Period](#a02--total-duration-processed-per-period)
  - [A03 · Period-over-Period Growth Rate](#a03--period-over-period-growth-rate)
  - [A04 · Channel Activation Rate](#a04--channel-activation-rate)
- [Section B — Output Mix & Content Type Trends](#section-b--output-mix--content-type-trends)
  - [B01 · Output Type Distribution](#b01--output-type-distribution)
  - [B02 · Input Type Distribution](#b02--input-type-distribution)
  - [B03 · Input Type Publish Affinity](#b03--input-type-publish-affinity)
  - [B04 · Output Type Growth Rate](#b04--output-type-growth-rate)
- [Section C — Publishing Funnel & Efficiency](#section-c--publishing-funnel--efficiency)
  - [C01 · Publish Rate ★](#c01--publish-rate-)
  - [C02 · Absolute Publish Gap](#c02--absolute-publish-gap)
  - [C03 · Ghost User Rate ★](#c03--ghost-user-rate-)
  - [C04 · Zero-Publisher Channel Rate ★](#c04--zero-publisher-channel-rate-)
  - [C05 · High-Volume Low-Publish Index](#c05--high-volume-low-publish-index)
- [Section D — Team / User / Language / Platform](#section-d--team--user--language--platform)
  - [D01 · Top Contributor Index ★](#d01--top-contributor-index-)
  - [D02 · User Concentration Index ★](#d02--user-concentration-index-)
  - [D03 · Language Publish Rate](#d03--language-publish-rate)
  - [D04 · Platform Publish Volume Share](#d04--platform-publish-volume-share)
  - [D05 · Platform Speciality Score ★](#d05--platform-speciality-score-)
  - [D06 · User Cross-Channel Breadth](#d06--user-cross-channel-breadth)
- [Section E — Data Quality & Governance](#section-e--data-quality--governance)
  - [E01 · Field Completeness Score](#e01--field-completeness-score)
  - [E02 · Unknown / Placeholder Rate](#e02--unknown--placeholder-rate)
  - [E03 · Duplicate Record Rate](#e03--duplicate-record-rate)
- [Section ★ — Core Channel KPIs (Original Set)](#section---core-channel-kpis-original-set)
  - [X01 · Channel Share in Published Output ★](#x01--channel-share-in-published-output-)
  - [X02 · Volume vs. Publish Output Scatter ★](#x02--volume-vs-publish-output-scatter-)
- [Data Sources Reference](#data-sources-reference)

---

## Document Overview

This README is the complete technical reference for all KPIs displayed in the Frammer AI Analytics Dashboard. It covers **21 non-redundant, non-overlapping KPIs** across **5 analytical domains** plus the original core KPI set (★).

Each KPI entry follows a consistent structure:

| Field | Description |
|---|---|
| **Definition** | What it measures and why it matters |
| **Formula** | Precise mathematical expression |
| **Formula Terms** | Every variable defined individually |
| **Worked Example** | Real CLIENT_1 numbers with calculation shown |
| **Actionable Insight** | What decision or action this KPI enables |

### Domain Map

| Section | Domain | KPIs |
|---|---|---|
| A | Usage & Adoption | A01–A04 |
| B | Output Mix & Content Type Trends | B01–B04 |
| C | Publishing Funnel & Efficiency | C01–C05 |
| D | Team / User / Language / Platform | D01–D06 |
| E | Data Quality & Governance | E01–E03 |
| ★ | Core Channel KPIs (Original Set) | X01–X02 |

> KPIs marked **★** are from the original set of 8 core KPIs defined by Frammer AI.

---

## Benchmark Quick-Reference

| KPI | Healthy | Concerning | Critical | Ref |
|---|---|---|---|---|
| Ghost User Rate | < 30% | 30–70% | > 70% | C03 |
| Zero-Publisher Channel Rate | < 20% | 20–50% | > 50% | C04 |
| Publish Rate | > 5% | 1–5% | < 1% | C01 |
| Top Contributor Index | < 30% | 30–50% | > 50% | D01 |
| User Concentration Index | < 25% | 25–50% | > 50% | D02 |
| Channel Share (single channel) | < 40% | 40–60% | > 60% | X01 |
| Platform Speciality Score | < 40% (diversified) | 40–70% (mixed) | > 70% (specialist) | D05 |

---

## Section A — Usage & Adoption

> Measures how actively the platform is being used: upload volumes, processing throughput, growth trends, and channel activation. These are the first metrics any executive or CS team should review to assess whether a client is growing with the platform.

---

### A01 · Upload Volume Trend

**Domain:** Usage & Adoption  
**Type:** Time-series trend

#### Definition

Upload Volume Trend measures the total number of raw videos uploaded by all users across all channels in each reporting period (day / week / month). It is the primary gauge of platform adoption growth or contraction over time. An upward trend indicates expanding usage; a sustained drop signals churn risk or seasonal variation. This KPI is the first chart any executive should see when evaluating whether a client is growing with the platform.

#### Formula

```
Upload Volume (period T) = Σ Uploaded Count for all channels in period T

Track T across consecutive periods to produce a time-series trend line.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Σ Uploaded Count` | Sum of the Uploaded Count column across all channel rows for the selected period T |
| `Period T` | The reporting window: day, calendar week, or calendar month. For monthly trending, group by year-month |

#### Worked Example

**Given:** Monthly data: Mar 2025 = 639 uploads, Apr 2025 = 533, Feb 2026 = 676

**Calculation:**
```
Upload Volume (Feb 2026) = 676
```

**Result:** 676 uploads in February 2026 — the highest single month on record.

**Meaning:** After dipping mid-year (Jul 2025: 284), uploads rebounded strongly in Jan–Feb 2026, suggesting a new campaign or onboarding cycle started at the turn of the year.

#### Actionable Insight

Pair with Period-over-Period Growth Rate (A03) to distinguish seasonal swings from structural trends. A spike in Upload Volume with no matching rise in Published Videos flags a widening publish gap.

---

### A02 · Total Duration Processed per Period

**Domain:** Usage & Adoption  
**Type:** Throughput metric

#### Definition

Total Duration Processed measures how many hours of AI-generated output content Frammer produced in a given period. Unlike Upload Volume (A01), which counts files, this KPI measures information throughput: a single 2-hour upload that spawns 90 minutes of AI summaries and clips contributes more to this metric than ten 30-second clips. It directly reflects the computational and editorial value delivered by the platform in each period.

#### Formula

```
Total Duration Processed (hrs) = Σ Created Duration (converted to hours)
                                   across all channels in period T

Conversion: hours + minutes/60 + seconds/3600
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Σ Created Duration` | Sum of Created Duration (HH:MM:SS) converted to decimal hours for all channels in period T |
| `Created Duration` | The total runtime of all AI-generated output videos, summed per channel per period |
| `Period T` | The reporting window (day / week / month) |

#### Worked Example

**Given:** February 2026 monthly data: Total Created Duration = 301:30:46 (HH:MM:SS)

**Calculation:**
```
301 hours + 30/60 + 46/3600 = 301.51 hours processed
```

**Result:** 301.5 hours of AI content processed in a single month.

**Meaning:** Over 12 full days of video content generated by Frammer's AI in one month, up from 191.5 hours in January 2026 — a **57% month-on-month increase** in throughput.

#### Actionable Insight

High Duration Processed with low Published Duration (see C02) confirms the platform is generating content that is not reaching audiences. Billing conversations should reference this metric to demonstrate AI value delivered.

---

### A03 · Period-over-Period Growth Rate

**Domain:** Usage & Adoption  
**Type:** Directional trend signal

#### Definition

Period-over-Period Growth Rate quantifies the percentage increase or decrease in a core usage metric — uploads, AI-created videos, or published videos — between two consecutive reporting periods. It converts raw volume trends into a single directional signal, making it easy to answer: *'Is this client growing, declining, or plateauing?'* Negative values are early warning signals; sustained positive values confirm healthy platform adoption.

#### Formula

```
Growth Rate (%) = ((Volume(T) − Volume(T−1)) / Volume(T−1)) × 100

Apply to: Upload Volume | Created Count | Published Count
Report separately for each metric.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Volume(T)` | The upload (or created / published) count in the current period T |
| `Volume(T−1)` | The upload (or created / published) count in the immediately preceding period T−1 |
| `× 100` | Scales the ratio to a percentage. Positive = growth; negative = decline |

#### Worked Example

**Given:** Total Uploaded: Dec 2025 = 194, Jan 2026 = 492

**Calculation:**
```
Growth Rate = ((492 − 194) / 194) × 100
            = (298 / 194) × 100
            = +153.6%
```

**Result:** Upload volume grew by **153.6% month-on-month** from December to January.

**Meaning:** January's surge followed December's sharp drop (−45% MoM). This volatility pattern suggests episodic campaign-driven usage rather than steady organic growth, warranting a conversation with the client about workflow consistency.

#### Actionable Insight

Apply this metric to all three funnel stages (uploads, created, published) separately. When Upload Growth is positive but Publish Growth is flat or negative, the publish gap is widening — a direct signal to prioritise client success intervention.

---

### A04 · Channel Activation Rate

**Domain:** Usage & Adoption  
**Type:** Portfolio health indicator

#### Definition

Channel Activation Rate measures what proportion of a client's registered channels are actually being used in a given period — defined as having at least one video uploaded. It distinguishes between channels that exist in the system and channels that are operationally live. A low activation rate means a significant portion of the client's contracted capacity is sitting idle, which has direct implications for licence value, onboarding effectiveness, and renewal risk.

#### Formula

```
Channel Activation Rate (%) = (Channels with Uploaded Count > 0 in period T
                                / Total registered channels) × 100
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Channels with Uploaded Count > 0` | Count of channels that have at least 1 upload in the selected period T |
| `Total registered channels` | Total count of distinct channels in the client's account |
| `× 100` | Converts to percentage |

#### Worked Example

**Given:** CLIENT_1 has 18 registered channels. In the full dataset period, all 18 channels show at least 1 upload.

**Calculation:**
```
Channel Activation Rate = (18 / 18) × 100 = 100%
```

**Result:** 100% activation rate across all channels over the full data period.

**Meaning:** All channels are at least nominally active. However, **12 of the 18 channels have Published Count = 0** (Zero-Publisher Channels, C04), so activation does not equal productive use. Activation Rate should always be paired with Publish Rate.

#### Actionable Insight

Track per-month activation to identify seasonal abandonment patterns. Channels inactive for 60+ days should trigger an automated CS alert.

---

## Section B — Output Mix & Content Type Trends

> Analyses the composition of what the AI is producing and what is being uploaded. Understanding the output and input mix helps tailor AI configuration to the client's content strategy and identify format-platform misalignments.

---

### B01 · Output Type Distribution

**Domain:** Output Mix  
**Type:** Composition metric

#### Definition

Output Type Distribution measures what fraction of all AI-generated videos belong to each output category — such as Full Package, Key Moments, Chapters, My Key Moments, Summary, and others. It reveals which AI features are being used most heavily by the client and whether the output mix aligns with their publishing strategy. Misalignment between output mix and publishing platform preference is an immediate coaching opportunity.

#### Formula

```
Output Type Share (%) = (Created Count for output type X / Total Created Count) × 100

All output type shares must sum to 100%.
Compute separately for count and for duration.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Created Count for type X` | Number of AI-generated videos of a specific output type (e.g. Key Moments = 6,377) |
| `Total Created Count` | Sum of Created Count across all output types in the dataset (= 14,914 for CLIENT_1) |
| `× 100` | Converts ratio to percentage |

#### Worked Example

**Given:** Key Moments: 6,377 created. Full Package: 4,453. Total: 14,914

**Calculation:**
```
Key Moments share  = (6,377 / 14,914) × 100 = 42.8%
Full Package share = (4,453 / 14,914) × 100 = 29.9%
```

**Result:** Key Moments dominates at 42.8%, followed by Full Package at 29.9%.

**Meaning:** Nearly half of all AI output is Key Moments, but Key Moments has only a **0.64% publish rate**. My Key Moments (8.3% share) has a **2.59% publish rate** — 4× better conversion. The client is generating the wrong output type at scale.

#### Actionable Insight

Cross-reference with output type publish rates (C01 by type) to identify the *'conversion champion'* output type. Rebalancing AI output generation toward high-converting types is the fastest lever for improving overall publish rate.

---

### B02 · Input Type Distribution

**Domain:** Output Mix  
**Type:** Content pipeline analysis

#### Definition

Input Type Distribution shows what proportion of uploaded raw videos belong to each content category — Interview, News Bulletin, Speech, Special Report, Discussion Show, Press Conference, Debate, Podcast, and so on. It maps the nature of the source material feeding the AI pipeline and helps tailor Frammer's AI configuration to the specific content mix a client produces.

#### Formula

```
Input Type Share (%) = (Uploaded Count for input type X / Total Uploaded Count) × 100

Compute for Uploaded Count (raw input) and separately for Created Count (AI output)
to see if the AI output mix mirrors the input mix.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Uploaded Count for type X` | Number of uploaded videos tagged as input type X (e.g. Interview = 1,299 uploads) |
| `Total Uploaded Count` | Sum of Uploaded Count across all input types (= 4,453 for CLIENT_1) |
| `× 100` | Converts to percentage |

#### Worked Example

**Given:** Interview: 1,299 uploaded. News Bulletin: 1,026. Total uploaded: 4,453

**Calculation:**
```
Interview share     = (1,299 / 4,453) × 100 = 29.2%
News Bulletin share = (1,026 / 4,453) × 100 = 23.0%
```

**Result:** Interview (29.2%) and News Bulletin (23.0%) together account for over half of all uploads.

**Meaning:** The client's content pipeline is dominated by interview and news content. AI templates and clip styles should be optimised for these two categories first.

#### Actionable Insight

When Input Type Distribution shifts month-over-month (e.g. Debate content surges), it may indicate a new editorial programme or live event season. Frammer's CS team can proactively offer tailored templates for emerging input types.

---

### B03 · Input Type Publish Affinity

**Domain:** Output Mix  
**Type:** Conversion quality signal

#### Definition

Input Type Publish Affinity measures the publish rate for each input type — i.e., what fraction of AI outputs generated from a given source content category are actually published. It answers the question: *'Which type of content does this team actually publish when Frammer processes it?'* High affinity means the team finds the AI outputs valuable enough to go live; low affinity suggests the output quality, format, or review workflow is not working for that content type.

#### Formula

```
Publish Affinity (%) = (Published Count for input type X / Created Count for input type X) × 100

Denominator = Created Count (AI output), NOT Uploaded Count.
Measures AI output conversion, not raw upload conversion.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Published Count for type X` | Number of videos of input type X that were published to any platform |
| `Created Count for type X` | Number of AI-generated outputs produced from input type X source material |
| `× 100` | Converts ratio to percentage |

#### Worked Example

**Given:** Discussion Show: Created = 79, Published = 3. News Bulletin: Created = 3,238, Published = 39

**Calculation:**
```
Discussion Show affinity = (3 / 79) × 100    = 3.80%
News Bulletin affinity   = (39 / 3,238) × 100 = 1.20%
```

**Result:** Discussion Show has 3.80% affinity — the highest of all input types.

**Meaning:** Despite being a small category, Discussion Show content is **3× more likely to be published** than News Bulletin content. The team should investigate what makes Discussion Show clips publication-ready and replicate that workflow for other types.

#### Actionable Insight

Sort all input types by affinity descending. The top 3 types are the client's *'sweet spot'* — content where Frammer delivers maximum value. Types with zero affinity (Sports Show, Podcast, Drama in this dataset) should be reviewed: is the AI template wrong, or is the team not using these outputs at all?

---

### B04 · Output Type Growth Rate

**Domain:** Output Mix  
**Type:** Feature adoption trend

#### Definition

Output Type Growth Rate tracks how the volume of each AI output category (Key Moments, Chapters, Summaries, etc.) is changing over time. It identifies which formats are gaining traction (growing) and which are being abandoned (declining). This is critical for product teams at Frammer who need to know which features are seeing adoption growth versus which are dormant, and for CS teams who need to course-correct clients drifting away from high-value output types.

#### Formula

```
Output Type Growth (%) = ((Created Count(T) − Created Count(T−1)) / Created Count(T−1)) × 100

Compute per output type, per period.
Requires time-stamped data (processed_at or uploaded_at field).
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Created Count(T)` | Number of AI outputs of a specific type in current period T |
| `Created Count(T−1)` | Number of AI outputs of the same type in the previous period T−1 |
| `× 100` | Scales to percentage. Positive = growing. Negative = declining |

#### Worked Example

**Given:** Key Moments created: Jan 2026 = 850, Feb 2026 = 1,120

**Calculation:**
```
Growth Rate = ((1,120 − 850) / 850) × 100
            = (270 / 850) × 100
            = +31.8%
```

**Result:** Key Moments output grew **31.8% month-over-month**.

**Meaning:** If Key Moments is also showing improving publish affinity, this combination of growing volume + improving conversion signals a healthy feature adoption arc. If publish affinity is flat, the growth is *'vanity volume'* — more AI output with no more reach.

#### Actionable Insight

Build a **2×2 matrix**: Volume Growth Rate (x-axis) vs Publish Affinity (y-axis).

| Quadrant | Meaning | Action |
|---|---|---|
| High Growth + High Affinity | Power feature | Invest and scale |
| High Growth + Low Affinity | Waste in progress | Constrain output |
| Low Growth + High Affinity | Stable value | Protect and optimise |
| Low Growth + Low Affinity | Dormant feature | Review or retire |

---

## Section C — Publishing Funnel & Efficiency

> The publishing funnel tracks what happens between AI content creation and actual audience delivery. These KPIs measure how much of the AI's output reaches the end platform, where the bottlenecks are, and which channels and users are failing to complete the workflow.

---

### C01 · Publish Rate ★

**Domain:** Publishing Funnel  
**Type:** Core funnel KPI · Original KPI 3

#### Definition

Publish Rate is the **single most important funnel metric**. It measures what fraction of all AI-generated output videos were actually published to an end platform. A low rate does not always mean bad content — it frequently signals workflow friction, missing platform credentials, approval bottlenecks, or teams using Frammer as a preview tool. It is the starting point for every funnel conversation with a client and is directly linked to the ROI they perceive from the platform.

#### Formula

```
Publish Rate (%) = (No. of Published Videos / Total AI-Created Videos) × 100

Denominator = Created Count, NOT Uploaded Count.
One upload produces multiple AI outputs; all must be counted.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `No. of Published Videos` | Count of videos with Published = Yes for this channel / type / period |
| `Total AI-Created Videos` | Sum of all AI-generated output videos (all types combined) for the same scope |
| `× 100` | Scales to percentage |

#### Worked Example

**Given:** CLIENT_1 total: Created = 14,914. Published = 111

**Calculation:**
```
Publish Rate = (111 / 14,914) × 100 = 0.74%
```

**Result:** Less than **1 in 135** AI-generated videos is ever published.

**Meaning:** The overall publish rate of 0.74% is extremely low. Even Channel A — the best performer — only achieves 1.50%. The platform is generating enormous AI value that never reaches an audience.

#### Benchmarks

| Rating | Threshold |
|---|---|
| 🔴 Critical Low | < 1% |
| 🟡 Low | 1–5% |
| 🟢 Moderate | 5–15% |
| ✅ High | > 15% |

#### Actionable Insight

Track this KPI at three levels: client-wide, per channel, and per output type. The per-type view (My Key Moments = 2.59% vs Chapters = 0.10%) reveals which formats should be prioritised in the AI pipeline to maximise publishing output.

---

### C02 · Absolute Publish Gap

**Domain:** Publishing Funnel  
**Type:** Scale impact metric

#### Definition

Absolute Publish Gap is the raw number of AI-generated videos that were created but never published — the *'content graveyard.'* Unlike Publish Rate (which is a percentage), this metric communicates the scale of wasted production in human terms. It is particularly powerful in executive conversations where percentages feel abstract but absolute counts resonate. It directly quantifies the upside opportunity.

#### Formula

```
Absolute Publish Gap = Total Created Videos − Total Published Videos

Duration version:
Absolute Gap (hrs) = Created Duration (hrs) − Published Duration (hrs)
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Total Created Videos` | Sum of all AI-generated output videos across all channels in the period |
| `Total Published Videos` | Sum of all videos actually published to any platform |

#### Worked Example

**Given:** CLIENT_1: Total Created = 14,914. Total Published = 111

**Calculation:**
```
Absolute Publish Gap = 14,914 − 111 = 14,803 videos
```

**Result:** **14,803 AI-generated videos** were created and never published.

**Meaning:** In duration terms — Created Duration ≈ 1,110 hours. Published Duration ≈ 8.2 hours. Over **1,100 hours of AI-processed content** (equivalent to 46 days of continuous video) never reached an audience.

#### Actionable Insight

Present both the count and duration versions to executives. The duration version (1,100+ hours unpublished) is far more visceral than the 0.74% rate. Segment the gap by channel to show which channels have the largest recoverable opportunity.

---

### C03 · Ghost User Rate ★

**Domain:** Publishing Funnel  
**Type:** User behaviour signal · Original KPI 1

#### Definition

Ghost User Rate measures the proportion of users on a given channel who have uploaded or processed content but have **never published a single video**. These users are *'ghosts'* — present in the system, consuming AI resources, but never completing the final step of the workflow. It is one of the strongest early-warning signals of a broken or inaccessible publishing pipeline.

#### Formula

```
Ghost User Rate (%) = (Users with Published Count = 0 / Total Users on Channel) × 100

A user is a 'ghost' if their cumulative Published Count = 0 across all time on that channel.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Users with Published Count = 0` | Count of distinct users in the channel whose total publications equal zero |
| `Total Users on Channel` | Count of all distinct users appearing in the channel's activity records |
| `× 100` | Scales to percentage |

#### Worked Example

**Given:** Channel D: 17 total users. All 17 have Published Count = 0.

**Calculation:**
```
Ghost User Rate = (17 / 17) × 100 = 100%
```

**Result:** Every single user in Channel D is a ghost — despite 221 uploads and 701 AI outputs.

**Meaning:** Channel D has a 100% ghost rate yet 71 videos were published externally. Publishing is happening **outside the user-tracked workflow** — a data integrity and attribution investigation is required.

#### Benchmarks

| Rating | Threshold |
|---|---|
| ✅ Healthy | < 30% |
| 🟡 Concerning | 30–70% |
| 🔴 Critical | > 70% |

#### Actionable Insight

Sort channels by Ghost User Rate descending. Channels at 100% ghost rate should be the first CS intervention targets. Use ghost rate + Platform Count (D04) together: a 100% ghost rate channel with 5 platforms connected is a *'broken last-mile'* emergency.

---

### C04 · Zero-Publisher Channel Rate ★

**Domain:** Publishing Funnel  
**Type:** Portfolio health signal · Original KPI 2

#### Definition

Zero-Publisher Channel Rate measures the proportion of all registered channels in a client portfolio that have **never published a single video** to any platform. A high rate means the client's publishing output is dangerously concentrated in a minority of channels — creating single-channel dependency risk. It also raises a billing question: are zero-publisher channels receiving the same service tier as active channels?

#### Formula

```
Zero-Publisher Channel Rate (%) = (Channels with Total Published Count = 0
                                    / Total Channels) × 100

'Zero-publisher' = Published Count summed across all users and all time = 0.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Channels with Published Count = 0` | Count of channels where sum of Published Count (all users, all time) equals zero |
| `Total Channels` | Count of all registered channels for this client |
| `× 100` | Scales to percentage |

#### Worked Example

**Given:** CLIENT_1: 18 total channels. Channels B, C, F, J, K, L, M, N, O, P, Q, R have Published Count = 0 across all users.

**Calculation:**
```
Zero-publisher channels = 12
Rate = (12 / 18) × 100 = 66.7%
```

**Result:** **66.7%** of CLIENT_1's channels have never published a single video.

**Meaning:** Two-thirds of the client's AI processing is flowing into channels that produce zero audience-facing content — a fundamental platform value-delivery problem.

#### Benchmarks

| Rating | Threshold |
|---|---|
| ✅ Healthy | < 20% |
| 🟡 Needs attention | 20–50% |
| 🔴 Critical | > 50% |

#### Actionable Insight

Any client above 50% zero-publisher rate is at **renewal risk**: they cannot articulate the value of their licence to stakeholders because the majority of their channels have nothing to show for it.

---

### C05 · High-Volume Low-Publish Index

**Domain:** Publishing Funnel  
**Type:** Intervention prioritisation flag

#### Definition

The High-Volume Low-Publish (HVLP) Index flags channels that consume large amounts of AI processing capacity but convert almost none of it to published output. These are the most expensive *'wasted potential'* channels — the bottleneck is entirely at the publish step. Identifying them allows CS teams to focus intervention where ROI recovery potential is highest.

#### Formula

```
HVLP Flag = 1  if  (Created Count ≥ Q3 of all channels)
               AND  (Publish Rate ≤ Q1 of publishing channels)

Q3 = 75th percentile of Created Count across all channels
Q1 = 25th percentile of Publish Rate among channels with Published Count > 0
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Created Count ≥ Q3` | Channel is in the top 25% by AI output volume |
| `Publish Rate ≤ Q1` | Channel's publish rate is in the bottom 25% among channels that have published at least once |
| `HVLP Flag` | Binary indicator: 1 = high-volume, low-publish channel; 0 = normal |

#### Worked Example

**Given:** Q3 of Created Count = 614. Q1 of Publish Rate (among active publishers) = 0.34%. Channel D: Created = 701, Publish Rate = 0.0%.

**Calculation:**
```
701 ≥ 614  ✓
0.0% ≤ 0.34%  ✓
→ HVLP Flag = 1
```

**Result:** Channel D is flagged as **High-Volume Low-Publish**.

**Meaning:** Channel D processes 701 AI outputs (above the 75th percentile) but publishes none of them through the user workflow. The 71 external publications bypass the internal system entirely. This is the highest-priority CS intervention target in the portfolio.

#### Actionable Insight

HVLP channels represent the best ROI recovery opportunity: AI output is already being created at scale. A single workflow fix (platform credential, approval process, user training) could immediately unlock publishing. Calculate potential uplift: if Channel D matched Channel A's 1.5% publish rate, it would add ~10 more published videos from existing output.

---

## Section D — Team / User / Language / Platform

> Analyses the human and technical distribution of work across teams, users, languages, and platforms. These KPIs identify key-person risks, team resilience, platform strategy alignment, and shared or test accounts that may pollute other metrics.

---

### D01 · Top Contributor Index ★

**Domain:** Team / User  
**Type:** Key-person risk indicator · Original KPI 6

#### Definition

The Top Contributor Index measures what fraction of a channel's total upload activity is driven by a single person — the highest-volume uploader. A high index means the content pipeline is effectively a single-operator workflow: if that person leaves, changes role, or loses access, the channel's content input could collapse immediately. It is a direct, human-readable measure of operational fragility.

#### Formula

```
Top Contributor Index (%) = (Uploads by top user in channel / Total channel uploads) × 100

Top user = user with max(Uploaded Count) in the channel.
Can be extended to top-3 cumulative share.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Uploads by top user` | Uploaded Count of the highest-contributing user in the channel |
| `Total channel uploads` | Sum of Uploaded Count across all users in the channel |
| `× 100` | Scales to percentage |

#### Worked Example

**Given:** Channel H: Total uploads = 89. Top user: vikas.s@moolya.com = 37 uploads.

**Calculation:**
```
Top Contributor Index = (37 / 89) × 100 = 41.6%
```

**Result:** One user controls **41.6%** of Channel H's entire upload volume.

**Meaning:** If vikas.s becomes unavailable, Channel H loses nearly half its content input instantly. The second-most active user (Kallol Pratim, 16 uploads, 18%) provides limited redundancy.

#### Benchmarks

| Rating | Threshold |
|---|---|
| ✅ Distributed team | < 30% |
| 🟡 Moderate risk | 30–50% |
| 🔴 High key-person risk | > 50% |

#### Actionable Insight

Build a risk register of channels where Top Contributor Index > 40%. Proactively encourage upload activity from secondary users through targeted training, shared account permissions reviews, and workflow documentation exercises.

---

### D02 · User Concentration Index ★

**Domain:** Team / User  
**Type:** Team health score · Original KPI 7

#### Definition

User Concentration Index extends Top Contributor Index by framing the same measurement as a team health score rather than a risk flag. The interpretation context changes: a **low index is a positive signal** (well-distributed, resilient team), while a high index is a red flag (over-reliance on one person). Used together with Ghost User Rate, it paints a complete picture of team engagement.

#### Formula

```
User Concentration Index (%) = (Max user upload count in channel / Total channel upload count) × 100

100% = one person does everything.
Lower values = more evenly distributed team activity.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Max user upload count` | Uploaded Count of the highest-contributing single user in the channel |
| `Total channel upload count` | Sum of all users' Uploaded Count for this channel |
| `× 100` | Scales to percentage |

#### Worked Example

**Given:** Channel A: Total uploads = 1,470. Top user (Chandan) = 247 uploads.

**Calculation:**
```
User Concentration Index = (247 / 1,470) × 100 = 16.8%
```

**Result:** Channel A has a **healthy concentration index of 16.8%** — the most distributed team in the portfolio.

**Meaning:** No single person dominates Channel A's upload activity. Contrast with Channel O (85.7%): one user accounts for nearly all activity, creating extreme single-point-of-failure risk.

#### Benchmarks

| Rating | Threshold |
|---|---|
| ✅ Distributed | < 25% |
| 🟡 Moderate | 25–50% |
| 🔴 Concentrated | > 50% |
| ⛔ Single operator | = 100% |

#### Actionable Insight

Channels in the concentrated range should be discussed in quarterly business reviews to ensure succession planning and documentation are in place.

---

### D03 · Language Publish Rate

**Domain:** Language / Platform  
**Type:** Localisation signal

#### Definition

Language Publish Rate measures the publish rate for each language in which content is uploaded and processed. It reveals whether certain language tracks have better or worse publishing workflows, and whether language-specific platform integrations are affecting the team's willingness or ability to publish.

#### Formula

```
Language Publish Rate (%) = (Published Count for language L / Created Count for language L) × 100

Compute per language code (en, hi, mix, etc.).
Compare to overall publish rate as baseline.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Published Count for L` | Number of videos in language L that were published to any platform |
| `Created Count for L` | Number of AI-generated outputs produced from source content in language L |
| `× 100` | Scales to percentage |

#### Worked Example

**Given:** English (en): Created = 8,861, Published = 91. Hindi (hi): Created = 6,021, Published = 20.

**Calculation:**
```
English publish rate = (91 / 8,861) × 100  = 1.03%
Hindi publish rate   = (20 / 6,021) × 100  = 0.33%
```

**Result:** English content is published at **3× the rate** of Hindi content.

**Meaning:** This gap may reflect fewer Hindi-language platform integrations, or that the Hindi editorial team faces more approval friction. Mixed-language content (mix) has 0% publish rate despite 29 created videos — likely a format or metadata issue.

#### Actionable Insight

For Hindi (second-largest by volume, 6,021 AI outputs, only 0.33% published), improving the publish rate to even 0.70% would **double the Hindi publishing output**. Investigate whether Hindi-specific platform templates and metadata fields are correctly configured.

---

### D04 · Platform Publish Volume Share

**Domain:** Language / Platform  
**Type:** Distribution strategy analysis

#### Definition

Platform Publish Volume Share shows what percentage of all externally published videos are distributed to each platform — YouTube, Reels, Shorts, Facebook, Instagram, LinkedIn, X, Threads. It reveals the client's de-facto distribution strategy and directly informs platform integration priority.

#### Formula

```
Platform Share (%) = (Published Videos on platform P / Total Published Videos) × 100

Sum over all platforms for a given client.
All platform shares must sum to 100%.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Published Videos on platform P` | Count of videos published to platform P |
| `Total Published Videos` | Sum of published video counts across all 8 tracked platforms for this client |
| `× 100` | Scales to percentage |

#### Worked Example

**Given:** CLIENT_1 external publishes: YouTube=29, Reels=26, Shorts=22, Facebook=9, Instagram=11, others=3. Total=100.

**Calculation:**
```
YouTube share = (29 / 100) × 100 = 29%
Reels share   = (26 / 100) × 100 = 26%
```

**Result:** YouTube and Reels together account for **55%** of all external publications.

**Meaning:** The client's distribution is dominated by YouTube long-form and Instagram Reels short-form. LinkedIn (0%), X (0%), and Threads (0%) are completely unused platforms.

#### Actionable Insight

Compare Platform Share with the output type mix (B01). If YouTube dominates distribution but Key Moments (short-form clips) dominates output type, there is a **format-platform mismatch**. Key Moments should be going to Reels and Shorts, not to YouTube.

---

### D05 · Platform Speciality Score ★

**Domain:** Language / Platform  
**Type:** Platform strategy indicator · Original KPI 8

#### Definition

Platform Speciality Score measures how concentrated a channel's external publishing is on its single most-used platform. A score near 100% means the channel has a single-platform strategy; a score below 40% means publishing is spread across many platforms. It surfaces *'Social Specialist'* channels with clear platform identities.

#### Formula

```
Platform Speciality Score (%) = (Videos on top platform / Total external published videos) × 100

Top platform = platform with the highest published video count for that channel.
Only compute for channels with Total Published > 0.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Videos on top platform` | Published count on the channel's most-used platform (max column value) |
| `Total external published videos` | Sum of all 8 platform column values for the channel |
| `× 100` | Scales to percentage |

#### Worked Example

**Given:** Channel G publishes: Reels=11, Shorts=2, Facebook=1. Total=14.

**Calculation:**
```
Speciality Score = (11 / 14) × 100 = 78.6%
```

**Result:** **78.6%** of Channel G's publishing is concentrated on Reels — a Reels-first strategy.

**Meaning:** Channel G is intentionally or organically a Reels specialist. Compare with Channel A (score = 36.8%): truly multi-platform, requiring broader AI configuration coverage.

#### Benchmarks

| Rating | Threshold |
|---|---|
| Strong speciality | > 70% |
| Mixed strategy | 40–70% |
| Diversified publisher | < 40% |

#### Actionable Insight

Channels with Speciality Score > 70% should have AI output settings **tuned specifically** for that platform's preferred format and duration. Channels < 40% need flexible templates that work across formats.

---

### D06 · User Cross-Channel Breadth

**Domain:** Team / User  
**Type:** Account classification signal

#### Definition

User Cross-Channel Breadth counts how many distinct channels each user appears in across the client's account. High breadth means a user is a *'roving contributor'* — often an internal champion, power user, or QA tester. Tracking this KPI helps distinguish production users from test/QA accounts, identifies potential internal champions for training programmes, and reveals whether channels share significant personnel.

#### Formula

```
Cross-Channel Breadth = Count of distinct channels where user U has Uploaded Count > 0

Breadth of 1 = silo user
Breadth > 5  = roving / shared user
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Distinct channels` | Count of unique Channel values for user U in the channel-user dataset |
| `Uploaded Count > 0` | User must have uploaded at least 1 video in the channel to count as 'active' there |

#### Worked Example

**Given:** User 'Subhash (moolya)' appears in 17 distinct channels with uploads in each.

**Calculation:**
```
Cross-Channel Breadth = 17 channels
```

**Result:** Subhash (moolya) is active in **17 of 18** total channels.

**Meaning:** This extreme breadth strongly suggests a shared account, QA/testing user, or internal Frammer admin performing system-wide testing. This account should be **excluded from user productivity metrics** to avoid polluting channel-level analysis.

#### Actionable Insight

Users with Cross-Channel Breadth ≥ 5 should be classified as shared/QA accounts and excluded from per-channel user productivity KPIs (D01, D02, C03). Failing to exclude them inflates user counts per channel and deflates per-user productivity figures.

---

## Section E — Data Quality & Governance

> These KPIs measure the integrity of the underlying data that powers all other analytics. Poor data quality silently corrupts every metric above. These three KPIs should be monitored continuously and should gate any dashboard metric that depends on the affected fields.

---

### E01 · Field Completeness Score

**Domain:** Data Quality  
**Type:** Metadata integrity metric

#### Definition

Field Completeness Score measures what fraction of video records in the dataset have every critical metadata field properly populated — not null, not empty, and not placeholder text such as *'Unknown'*. Every missing field is a gap in reporting accuracy and a potential billing error. Fields such as Team Name, Published Platform, and Published URL are particularly critical.

#### Formula

```
Field Completeness Score (%) = (Records where field F is populated / Total records) × 100

A 'populated' value is:
  - Non-null
  - Non-empty
  - Not equal to 'Unknown', 'N/A', or similar placeholders
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Records where field F is populated` | Count of video records where field F has a valid, non-placeholder value |
| `Total records` | Total number of video records in the dataset (= 14,918 for CLIENT_1) |
| `× 100` | Converts to percentage. 100% = no missing data |

#### Worked Example

**Given:** CLIENT_1 video_list dataset: 14,918 records. 'Team Name' field: 14,812 records have 'Unknown', null, or empty. Only 106 have a real team name.

**Calculation:**
```
Team Name Completeness = (106 / 14,918) × 100 = 0.71%
```

**Result:** Team Name is **0.71% complete** — effectively missing from the entire dataset.

**Meaning:** Team-level reporting is impossible with only 0.71% coverage. Published Platform is also 0.22% complete. Platform-level analytics are built almost entirely on the channel-wise-publishing.csv aggregate — the row-level data is unreliable.

#### Actionable Insight

Prioritise fixing the three most impactful missing fields: **Team Name** (blocks team attribution), **Published Platform** (blocks platform analytics), and **Published URL** (blocks content verification). Each field should have a data quality SLA — e.g., Team Name ≥ 80% completeness within 90 days.

---

### E02 · Unknown / Placeholder Rate

**Domain:** Data Quality  
**Type:** Soft corruption detector

#### Definition

Unknown / Placeholder Rate specifically targets records that appear populated but contain meaningless values — *'Unknown'*, *'N/A'*, *'None'*, *'—'*, or similar placeholder text. These records pass null checks but pollute analysis. This KPI is the second layer of data quality monitoring, catching soft corruption that completeness checks miss.

#### Formula

```
Unknown Rate (%) = (Records where field F = 'Unknown' or placeholder
                    / Total records with non-null F) × 100

Common placeholders to check: 'Unknown', 'unknown', 'N/A', 'none', 'None', ''
Apply per field.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Records with field F = 'Unknown'` | Count of records where field F is non-null but contains a recognised placeholder value |
| `Total records with non-null F` | Count of records where field F is not null (regardless of value) |
| `× 100` | Scales to percentage |

#### Worked Example

**Given:** 14,918 total records. 'Team Name': 14,779 are non-null but contain 'Unknown'. 33 are null. 106 have real values.

**Calculation:**
```
Unknown Rate = (14,779 / (14,918 − 33)) × 100
             = (14,779 / 14,885) × 100
             = 99.3%
```

**Result:** **99.3%** of non-null Team Name values are the placeholder *'Unknown'*.

**Meaning:** The Team Name field is nominally populated (only 33 nulls) but functionally useless (99.3% placeholder). Any analytics built on Team Name will be invalid without data cleaning or enrichment.

#### Actionable Insight

Build an automated Unknown Rate monitor that runs after each data ingestion cycle. Any field crossing **20% Unknown Rate** should trigger a data governance alert. For Team Name: the fix is likely a Frammer-side onboarding step — teams should be required to set their workspace team name during channel setup.

---

### E03 · Duplicate Record Rate

**Domain:** Data Quality  
**Type:** Pipeline integrity check

#### Definition

Duplicate Record Rate measures the fraction of video records that share the same Video ID — indicating either a data pipeline error (the same video was ingested twice), a system reprocessing event, or a genuine repost. Even a small number of duplicate IDs can corrupt funnel metrics: if a Published = Yes video appears twice, it inflates the published count.

#### Formula

```
Duplicate Rate (%) = (Records with a Video ID that appears more than once / Total records) × 100

A Video ID is 'duplicate' if count(Video ID) > 1 in the dataset.
Count ALL records sharing that ID, not just the extras.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Records with duplicate Video ID` | Count of all records whose Video ID value appears more than once in the dataset |
| `Total records` | Total row count in the video-level dataset |
| `× 100` | Scales to percentage |

#### Worked Example

**Given:** CLIENT_1 video_list: 14,918 records. 5 Video IDs appear more than once (found by pandas `.duplicated()` check).

**Calculation:**
```
Duplicate Rate = (5 / 14,918) × 100 = 0.033%
```

**Result:** **0.033% duplicate rate** — very low, but 5 records are affected.

**Meaning:** 5 records may be double-counted in funnel metrics. If any of these are Published = Yes, the published count is overstated.

#### Actionable Insight

Even a 0.033% rate is worth flagging in a production analytics system because duplicates compound: if a Video ID appears twice and is published, the published count, the publish rate numerator, and channel share calculations are all affected. Add a **deduplication step** (keep latest record per Video ID) to all ETL pipelines.

---

## Section ★ — Core Channel KPIs (Original Set)

> These two KPIs were the original core metrics defined by Frammer AI. X01 provides the portfolio concentration view; X02 is the flagship visual diagnostic that should open every client QBR presentation.

---

### X01 · Channel Share in Published Output ★

**Domain:** Portfolio Concentration  
**Type:** Concentration risk metric · Original KPI 5

#### Definition

Channel Share in Published Output measures what percentage of a client's total published video volume is driven by each individual channel. It is the portfolio-level concentration metric: if one channel dominates, any disruption to that channel collapses the client's entire publishing footprint. It also identifies *'invisible'* channels — those that consume AI resources but contribute zero to the client's actual audience reach.

#### Formula

```
Channel Share (%) = (Published Count for channel C / Sum of Published Count across all channels) × 100

All channel shares sum to 100%.
Channels with Published Count = 0 have 0% share.
```

#### Formula Terms

| Term | Definition |
|---|---|
| `Published Count for C` | Total published videos for channel C across all users and all time |
| `Sum across all channels` | Grand total of published videos for all channels in the client account |
| `× 100` | Scales to percentage |

#### Worked Example

**Given:** Total published = 111. Channel A = 71, B = 19, C = 14, all others = 7.

**Calculation:**
```
Channel A share       = (71 / 111) × 100 = 64.0%
Top 3 combined share  = (71 + 19 + 14) / 111 × 100 = 93.7%
```

**Result:** Three channels account for **93.7%** of all published output. Channel A alone: **64%**.

**Meaning:** The client's publishing success is dangerously concentrated in Channel A. A single key-user departure or platform credential issue in Channel A would drop total publishing output by nearly two-thirds overnight.

#### Benchmarks

| Rating | Threshold |
|---|---|
| ✅ Healthy portfolio | No single channel > 40% |
| 🟡 At risk | Single channel at 40–60% |
| 🔴 Critical concentration | Single channel > 60% |

#### Actionable Insight

Set a portfolio health target: no single channel should exceed 40% share. If a channel exceeds 50%, it becomes a critical concentration risk requiring dedicated CS attention to activate secondary channels.

---

### X02 · Volume vs. Publish Output Scatter ★

**Domain:** Portfolio Visual  
**Type:** Multi-dimensional visual diagnostic · Original KPI 4

#### Definition

Volume vs. Publish Output Scatter is a multi-dimensional **visual KPI** that plots every channel simultaneously across three dimensions. It is not a single number — it is a diagnostic chart that makes structural patterns immediately visible. It is the most effective single chart for an executive overview presentation.

#### Chart Specification

```
X-axis    = Created Count per channel     (AI output volume / potential)
Y-axis    = Published Count per channel   (real audience reach achieved)
Bubble    ∝ √(Uploaded Count)             (input effort; large = heavy uploader)

Color coding:
  🟢 Green  = Publish Rate ≥ 1%    (active publisher)
  🟡 Amber  = Publish Rate > 0% and < 1%  (critical low)
  🔴 Red    = Publish Rate = 0%    (zero-publisher channel)
```

#### Formula Terms

| Term | Definition |
|---|---|
| `X-axis (Created Count)` | Total AI-generated output videos per channel — represents AI pipeline potential |
| `Y-axis (Published Count)` | Total videos published to any platform — represents real audience reach achieved |
| `Bubble size ∝ √(Uploaded)` | Proportional to the square root of upload count — encodes input effort |
| `Color coding` | Green ≥ 1% publish rate · Amber >0% but <1% · Red = 0% (zero-publisher) |

#### Worked Example

**Given:** Channel A: Created=4,725, Published=71. Channel B: Created=4,251, Published=19. Channel L: Created=216, Published=0.

**Plotted positions:**
```
Channel A → (4725, 71)  — large green bubble
Channel B → (4251, 19)  — large amber bubble
Channel L → (216, 0)    — small red bubble
```

**Result:** The chart shows nearly all channels clustered near Y=0, with only A, B, and C visible above the baseline.

**Meaning:** The overwhelming pattern is a **'wall of red'** at Y=0 — channels with thousands of AI outputs and zero published content. This pattern is impossible to communicate as powerfully through a table of numbers.

#### Benchmark Position

| Ideal | Worst |
|---|---|
| High X + High Y (upper-right quadrant) | High X + Y = 0 (lower-right) |

#### Actionable Insight

This chart should open every client QBR presentation. The ideal trajectory for any channel is **moving upward and to the right** over successive quarters. Channels moving right (more AI output) but staying at Y=0 are wasting investment.

---

## Data Sources Reference

All KPIs in this document are computed from the following data files provided in the CLIENT_1 anonymised dataset:

| File | Used For |
|---|---|
| `CLIENT_1_combined_data.csv` | Channel-level aggregates: Uploaded Count, Created Count, Published Count |
| `combined_data_by_channel_and_user.csv` | User-level breakdown per channel: supports D01, D02, D06, C03 |
| `video_list_data_obfuscated.csv` | Row-level video records: supports E01, E02, E03, B-series, C01 |
| `channel-wise-publishing.csv` | Platform-specific publish counts per channel: supports D04, D05, X01, X02 |
| `channel-wise-publishing_duration.csv` | Duration-weighted platform analysis: companion to D04, D05 |

---

> **Classification:** Internal / Competition Use Only  
> Frammer AI Pvt Limited · CIN U62099DL2023PTC411035  
> 207 Okhla Industrial Estate, New Delhi – 110020  
> corp@frammer.com · +91 97112 04165
