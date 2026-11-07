"""
retirement_model.py
-------------------
Step 5 of the Pension Member Insights project.

Question: Which ACTIVE members are most likely to retire soon?

Idea:
    1. Look at people aged 55+. Some already RETIRED, some still WORK.
    2. The model learns the difference between them.
    3. We use the model on active members and give each one a
       "retirement risk" score from 0% to 100%.

How to run it:
    pip install scikit-learn
    python retirement_model.py
"""

import sqlite3

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------
# STEP 1: Load the members and calculate their age
# ---------------------------------------------------------------
conn = sqlite3.connect("pension.db")
members = pd.read_sql_query("SELECT * FROM members", conn)
conn.close()

today = pd.Timestamp("2026-10-01")
members["age"] = (today - pd.to_datetime(members["birth_date"])).dt.days / 365.25
members["age"] = members["age"].round(1)

# ---------------------------------------------------------------
# STEP 2: Choose the people the model learns from
# ---------------------------------------------------------------
# Only people aged 55+ who are Active or Retired
learn = members[(members["age"] >= 55) & (members["status"] != "Deferred")]

# The answer we want to predict: 1 = retired, 0 = still working
answer = (learn["status"] == "Retired").astype(int)

# ---------------------------------------------------------------
# STEP 3: Choose the information the model can use
# ---------------------------------------------------------------
# get_dummies turns text into 0/1 columns, because models only read numbers.
# Example: job_category "Management" becomes a column "job_Management" = 1
def make_features(df):
    return pd.get_dummies(df[["age", "job_category", "employment_type"]],
                          prefix=["job", "type"], dtype=int)

features = make_features(learn)

# ---------------------------------------------------------------
# STEP 4: Split into "study" (80%) and "exam" (20%)
# ---------------------------------------------------------------
# The model studies on 80%. Then we test it on the 20% it never saw.
X_study, X_exam, y_study, y_exam = train_test_split(
    features, answer, test_size=0.2, random_state=42)

# ---------------------------------------------------------------
# STEP 5: Train the model
# ---------------------------------------------------------------
model = LogisticRegression(max_iter=1000)
model.fit(X_study, y_study)

# ---------------------------------------------------------------
# STEP 6: Check the exam score
# ---------------------------------------------------------------
score = model.score(X_exam, y_exam)
print(f"The model was right {score:.0%} of the time on new people.")

# ---------------------------------------------------------------
# STEP 7: Give every active member aged 50+ a risk score
# ---------------------------------------------------------------
active = members[(members["status"] == "Active") & (members["age"] >= 50)].copy()

active_features = make_features(active).reindex(columns=features.columns, fill_value=0)
active["retirement_risk"] = model.predict_proba(active_features)[:, 1].round(2)

active["risk_level"] = "Low"
active.loc[active["retirement_risk"] >= 0.3, "risk_level"] = "Medium"
active.loc[active["retirement_risk"] >= 0.6, "risk_level"] = "High"

print("\nActive members (50+) by risk level:")
print(active["risk_level"].value_counts().to_string())

# ---------------------------------------------------------------
# STEP 8: Save the results for Power BI
# ---------------------------------------------------------------
active[["member_id", "age", "job_category", "retirement_risk", "risk_level"]] \
    .sort_values("retirement_risk", ascending=False) \
    .to_csv("powerbi/retirement_risk.csv", index=False)

print("\nSaved powerbi/retirement_risk.csv")
