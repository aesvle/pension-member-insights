"""
run_queries.py
--------------
Step 3 of the Pension Member Insights project.

What this script does:
    Runs every query in queries.sql on pension.db and prints the results
    as nice tables. It also saves each result as a CSV file in the
    "results" folder (we will use these later in Power BI and Excel).

How to run it:
    python run_queries.py
"""

import os
import sqlite3

import pandas as pd

os.makedirs("results", exist_ok=True)

with open("queries.sql", encoding="utf-8") as f:
    sql_text = f.read()

# Each query ends with ";" so we split the file into separate queries
queries = [q.strip() for q in sql_text.split(";") if "SELECT" in q.upper()]

conn = sqlite3.connect("pension.db")

for number, query in enumerate(queries, start=1):
    result = pd.read_sql_query(query, conn)
    print(f"\n========== Q{number} ==========")
    print(result.to_string(index=False))
    result.to_csv(f"results/q{number}.csv", index=False)

conn.close()
print("\nAll results saved in the 'results' folder.")
