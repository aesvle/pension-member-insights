"""
load_to_sql.py
--------------
Step 2 of the Pension Member Insights project.

What this script does:
    1. Reads the CSV files from the "data" folder
    2. CLEANS the data (fixes the problems we planted on purpose)
    3. Saves everything into a SQL database file called pension.db

Why SQLite?
    SQLite is a real SQL database that lives in ONE file.
    No installation, no server, no password. Python already has it built in.

How to run it:
    python load_to_sql.py
"""

import sqlite3

import pandas as pd

# ---------------------------------------------------------------------------
# 1. READ THE CSV FILES
# ---------------------------------------------------------------------------
employers = pd.read_csv("data/employers.csv")
members = pd.read_csv("data/members.csv")

print(f"Rows before cleaning: {len(members)}")

# ---------------------------------------------------------------------------
# 2. CLEAN THE DATA
# ---------------------------------------------------------------------------
# Problem 1: duplicate rows (the same member appears twice)
duplicates = members.duplicated().sum()
members = members.drop_duplicates()
print(f"  Removed {duplicates} duplicate rows")

# Problem 2: wrong capitalization ("registered nurse" vs "Registered Nurse")
wrong_case = (members["job_category"] == "registered nurse").sum()
members["job_category"] = members["job_category"].str.title()
print(f"  Fixed {wrong_case} job titles with wrong capitalization")

# Problem 3: missing salary
# We fill it with the MEDIAN salary of people with the same job and
# employment type. (Median = middle value, it is not affected by extreme values.)
missing = members["annual_salary"].isna().sum()
members["annual_salary"] = members.groupby(["job_category", "employment_type"])[
    "annual_salary"].transform(lambda s: s.fillna(s.median()))
print(f"  Filled {missing} missing salaries with the median for that job")

print(f"Rows after cleaning: {len(members)}")

# ---------------------------------------------------------------------------
# 3. SAVE INTO A SQL DATABASE
# ---------------------------------------------------------------------------
conn = sqlite3.connect("pension.db")

# "replace" means: if the table already exists, delete it and create it again
employers.to_sql("employers", conn, if_exists="replace", index=False)
members.to_sql("members", conn, if_exists="replace", index=False)

conn.close()
print("\nSaved tables 'employers' and 'members' into pension.db")
