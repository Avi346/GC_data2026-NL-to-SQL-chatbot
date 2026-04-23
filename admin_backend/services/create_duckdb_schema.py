import pandas as pd
import duckdb
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "admin")

def _data_file(name: str) -> str:
    return os.path.join(DATA_DIR, name)

# Database initialization
DB_PATH = os.getenv(
    "ADMIN_DB_PATH",
    os.getenv("DB_PATH", _data_file("frammer_analytics.duckdb")),
)
if not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, DB_PATH)
con = duckdb.connect(database=DB_PATH)

def time_to_seconds(time_str):
    """Converts hh:mm:ss or mm:ss to integer seconds."""
    if pd.isna(time_str) or not isinstance(time_str, str):
        return 0
    parts = time_str.split(':')
    if len(parts) == 3:
        h, m, s = [int(p) if p.isdigit() else 0 for p in parts]
        return h * 3600 + m * 60 + s
    elif len(parts) == 2:
        m, s = [int(p) if p.isdigit() else 0 for p in parts]
        return m * 60 + s
    return 0

# 1. Initialize empty lists to collect OBT data
obt_rows = []

# --- Helper functions to parse aggregated CSVs ---

def process_file_with_metrics(df, focus_name, dim_col, dim_name):
    """Generic processor for files with standard metrics."""
    global obt_rows
    # Convert standard duration columns
    for col in df.columns:
        if 'Duration' in col:
            df[col + '_Seconds'] = df[col].apply(time_to_seconds)

    for _, row in df.iterrows():
        obt_row = {
            'metric_focus': focus_name,
            'time_period': 'Overall',
            'channel_name': row.get('Channel', None),
            'user_name': row.get('User', None),
            'content_category': row[dim_col] if focus_name not in ['By Channel', 'By User'] else None,
            'uploaded_count': row.get('Uploaded Count', 0),
            'created_count': row.get('Created Count', 0),
            'published_count': row.get('Published Count', 0),
            'uploaded_duration_seconds': row.get('Uploaded Duration (hh:mm:ss)_Seconds', 0),
            'created_duration_seconds': row.get('Created Duration (hh:mm:ss)_Seconds', 0),
            'published_duration_seconds': row.get('Published Duration (hh:mm:ss)_Seconds', 0),
        }
        obt_rows.append(obt_row)

# --- Process specific CSVs into OBT format ---

# Read By Input Type
df = pd.read_csv(_data_file('combined_data(2025-3-1-2026-2-28) by input type.csv'))
process_file_with_metrics(df, 'By Input Type', 'Input Type', 'content_category')

# Read By Output Type
df = pd.read_csv(_data_file('combined_data(2025-3-1-2026-2-28) by output type.csv'))
process_file_with_metrics(df, 'By Output Type', 'Output Type', 'content_category')

# Read By Language
df = pd.read_csv(_data_file('combined_data(2025-3-1-2026-2-28) by language.csv'))
process_file_with_metrics(df, 'By Language', 'Language', 'content_category')

# Read By User
df = pd.read_csv(_data_file('combined_data(2025-3-1-2026-2-28) by user.csv'))
process_file_with_metrics(df, 'By User', 'User', 'user_name')

# Read By Channel and User
df = pd.read_csv(_data_file('combined_data(2025-3-1-2026-2-28) by channel and user.csv'))
process_file_with_metrics(df, 'By Channel and User', 'Channel', 'channel_name')

# Read Overall Client 1
df = pd.read_csv(_data_file('CLIENT 1 combined_data(2025-3-1-2026-2-28).csv'))
process_file_with_metrics(df, 'Overall Client Summary', 'Channel', 'channel_name')

# Read Monthly Duration
# Format: "Month","Total Uploaded Duration","Total Created Duration","Total Published Duration"
df_dur = pd.read_csv(_data_file('month-wise-duration.csv'))
for col in df_dur.columns:
    if 'Duration' in col:
        df_dur[col + '_Seconds'] = df_dur[col].apply(time_to_seconds)

df_chart = pd.read_csv(_data_file('monthly-chart.csv'))
# Format: "Month","Total Uploaded","Total Created","Total Published"
df_monthly = pd.merge(df_dur, df_chart, on='Month', how='outer')

for _, row in df_monthly.iterrows():
    obt_rows.append({
        'metric_focus': 'Monthly Overall',
        'time_period': row['Month'],
        'uploaded_count': row.get('Total Uploaded', 0),
        'created_count': row.get('Total Created', 0),
        'published_count': row.get('Total Published', 0),
        'uploaded_duration_seconds': row.get('Total Uploaded Duration_Seconds', 0),
        'created_duration_seconds': row.get('Total Created Duration_Seconds', 0),
        'published_duration_seconds': row.get('Total Published Duration_Seconds', 0),
    })

# Read Channel wise publishing
# Format: Channels,Facebook,Instagram,Linkedin,Reels,Shorts,X,Youtube,Threads
df_plat = pd.read_csv(_data_file('channel-wise-publishing.csv'))
df_plat_dur = pd.read_csv(_data_file('channel-wise-publishing duration.csv'))

df_plat_merged = pd.merge(df_plat, df_plat_dur, on='Channels', how='outer')

for _, row in df_plat_merged.iterrows():
    obt_rows.append({
        'metric_focus': 'Channel Platform Breakdown',
        'time_period': 'Overall',
        'channel_name': row['Channels'],
        # Store individual platform counts and durations directly into the specific columns
        'platform_facebook_count': row.get('Facebook', 0),
        'platform_instagram_count': row.get('Instagram', 0),
        'platform_linkedin_count': row.get('Linkedin', 0),
        'platform_reels_count': row.get('Reels', 0),
        'platform_shorts_count': row.get('Shorts', 0),
        'platform_x_count': row.get('X', 0),
        'platform_youtube_count': row.get('Youtube', 0),
        'platform_threads_count': row.get('Threads', 0),
        
        'platform_facebook_duration_seconds': time_to_seconds(row.get('Facebook Duration', '0')),
        'platform_instagram_duration_seconds': time_to_seconds(row.get('Instagram Duration', '0')),
        'platform_linkedin_duration_seconds': time_to_seconds(row.get('Linkedin Duration', '0')),
        'platform_reels_duration_seconds': time_to_seconds(row.get('Reels Duration', '0')),
        'platform_shorts_duration_seconds': time_to_seconds(row.get('Shorts Duration', '0')),
        'platform_x_duration_seconds': time_to_seconds(row.get('X Duration', '0')),
        'platform_youtube_duration_seconds': time_to_seconds(row.get('Youtube Duration', '0')),
        'platform_threads_duration_seconds': time_to_seconds(row.get('Threads Duration', '0')),
    })

# --- Save OBT to DuckDB ---
df_aggregate_metrics_obt = pd.DataFrame(obt_rows)

# Drop any potential old table to ensure clean refresh
con.execute("DROP TABLE IF EXISTS aggregate_metrics_obt")

# Workaround for DuckDB/Pandas type issues: Save to CSV and load
temp_csv_obt = "temp_aggregate_metrics_obt.csv"
df_aggregate_metrics_obt.to_csv(temp_csv_obt, index=False)
try:
    con.execute(f"CREATE TABLE aggregate_metrics_obt AS SELECT * FROM read_csv_auto('{temp_csv_obt}')")
    print(f"Created table 'aggregate_metrics_obt' with {len(df_aggregate_metrics_obt)} rows.")
finally:
    if os.path.exists(temp_csv_obt):
        os.remove(temp_csv_obt)

# --- Process Base Granular Dat ---
df_raw = pd.read_csv(_data_file('video_list_data_obfuscated.csv'))

# Clean Column Names (snake_case)
df_raw.columns = (
    df_raw.columns.str.strip().str.lower()
    .str.replace(' ', '_')
    .str.replace('(', '')
    .str.replace(')', '')
)

# Convert string Yes/No to boolean
if 'published' in df_raw.columns:
    df_raw['is_published'] = df_raw['published'].apply(lambda x: True if str(x).strip().lower() == 'yes' else False)
    df_raw = df_raw.drop(columns=['published'])

# Save to DuckDB
con.execute("DROP TABLE IF EXISTS video_details")

# Workaround for DuckDB/Pandas type issues: Save to CSV and load
temp_csv_raw = "temp_video_details.csv"
df_raw.to_csv(temp_csv_raw, index=False)
try:
    con.execute(f"CREATE TABLE video_details AS SELECT * FROM read_csv_auto('{temp_csv_raw}')")
    print(f"Created table 'video_details' with {len(df_raw)} rows.")
finally:
    if os.path.exists(temp_csv_raw):
        os.remove(temp_csv_raw)

con.close()
print(f"Successfully created DuckDB database at: {DB_PATH}")
