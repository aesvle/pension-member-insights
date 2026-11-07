"""
export_for_powerbi.py
---------------------
Step 4 of the Pension Member Insights project.

What this script does:
    Takes the CLEAN data from pension.db and adds helpful columns
    (age, age group, years until retirement, retirement window).
    Then it saves 2 CSV files in the "powerbi" folder.
    Power BI will read these 2 files.

Why do this in SQL/Python and not in Power BI?
    It keeps Power BI simple. All the logic lives in one place (SQL),
    which is what real data teams do.

How to run it:
    python export_for_powerbi.py
"""

import os
import sqlite3

import pandas as pd

os.makedirs("powerbi", exist_ok=True)
conn = sqlite3.connect("pension.db")

TYPICAL_RETIREMENT_AGE = 60   # we found this in Q2

members_query = f"""
WITH base AS (
    SELECT
        m.*,
        ROUND((julianday('2026-10-01') - julianday(m.birth_date)) / 365.25, 1) AS age
    FROM members m
)
SELECT
    *,
    CASE
        WHEN age < 30 THEN '1. Under 30'
        WHEN age < 40 THEN '2. 30-39'
        WHEN age < 50 THEN '3. 40-49'
        WHEN age < 60 THEN '4. 50-59'
        ELSE '5. 60+'
    END AS age_group,
    CASE
        WHEN status <> 'Active' THEN NULL
        WHEN {TYPICAL_RETIREMENT_AGE} - age < 0 THEN 0
        ELSE ROUND({TYPICAL_RETIREMENT_AGE} - age, 1)
    END AS years_to_retirement,
    CASE
        WHEN status <> 'Active' THEN 'Not active'
        WHEN age >= {TYPICAL_RETIREMENT_AGE} THEN '1. Eligible now'
        WHEN age >= {TYPICAL_RETIREMENT_AGE - 5} THEN '2. Within 5 years'
        WHEN age >= {TYPICAL_RETIREMENT_AGE - 10} THEN '3. In 5 to 10 years'
        ELSE '4. More than 10 years'
    END AS retirement_window
FROM base
"""

members = pd.read_sql_query(members_query, conn)
employers = pd.read_sql_query("SELECT * FROM employers", conn)
conn.close()

members.to_csv("powerbi/members_clean.csv", index=False)
employers.to_csv("powerbi/employers.csv", index=False)

print(f"Saved powerbi/members_clean.csv ({len(members)} rows)")
print(f"Saved powerbi/employers.csv ({len(employers)} rows)")
print("\nActive members by retirement window:")
print(members[members["status"] == "Active"]["retirement_window"].value_counts().sort_index().to_string())