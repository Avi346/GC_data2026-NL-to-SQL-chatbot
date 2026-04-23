import duckdb
import pandas as pd
import os

DB_PATH = 'frammer_analytics.duckdb'

print(f"Connecting to {DB_PATH}...\n")
con = duckdb.connect(database=DB_PATH)

# Get list of tables
tables = con.execute("SHOW TABLES").df()['name'].tolist()
print(f"Found {len(tables)} tables: {tables}\n")

for table in tables:
    print(f"--- Schema for '{table}' ---")
    # Print the schema (column names and types)
    schema_df_formatted = con.execute(f"DESCRIBE {table}").df()[['column_name', 'column_type']]
    print(schema_df_formatted.to_string(index=False))
    print("\n")
    
    # Export first 100 rows to CSV
    export_filename = f"SAMPLE_{table}.csv"
    print(f"Exporting top 100 rows of '{table}' to {export_filename}...")
    sample_df = con.execute(f"SELECT * FROM {table} LIMIT 100").df()
    sample_df.to_csv(export_filename, index=False)
    print("Done.\n")

print("Finished exporting sample CSVs. You can now open them in your current folder.")
con.close()
