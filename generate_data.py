"""
generate_data.py
----------------
Step 1 of the Pension Member Insights project.

What this script does:
    It creates FAKE (synthetic) but realistic data about members of a
    healthcare pension plan in Ontario. Real member data is private,
    so we make our own data that behaves like the real thing.

What it creates (in the "data" folder):
    employers.csv  -> 25 hospitals and healthcare employers
    members.csv    -> 5,000 pension plan members

How to run it:
    python generate_data.py
"""

import os
from datetime import date

import numpy as np
import pandas as pd

# A "seed" makes the random numbers the same every time you run the script.
# This way your results never change by surprise.
rng = np.random.default_rng(seed=42)

TODAY = date(2026, 10, 1)      # the "as of" date of our data
NUM_MEMBERS = 5000
NUM_EMPLOYERS = 25

os.makedirs("data", exist_ok=True)

# ---------------------------------------------------------------------------
# 1. EMPLOYERS (hospitals, long-term care homes, clinics)
# ---------------------------------------------------------------------------
regions = ["Toronto", "Central", "East", "West", "North"]
employer_types = ["Hospital", "Hospital", "Hospital", "Long-Term Care", "Community Health"]

employers = []
for i in range(1, NUM_EMPLOYERS + 1):
    region = regions[(i - 1) % len(regions)]
    emp_type = employer_types[rng.integers(0, len(employer_types))]
    employers.append({
        "employer_id": f"E{i:03d}",                       # E001, E002, ...
        "employer_name": f"{region} {emp_type} {i:02d}",  # e.g. "Toronto Hospital 01"
        "employer_type": emp_type,
        "region": region,
    })
employers_df = pd.DataFrame(employers)

# ---------------------------------------------------------------------------
# 2. MEMBERS
# ---------------------------------------------------------------------------
# Job categories with: share of members, salary range (min, max)
job_info = {
    "Registered Nurse":           (0.35, 75000, 115000),
    "Registered Practical Nurse": (0.15, 55000, 75000),
    "Personal Support Worker":    (0.15, 40000, 55000),
    "Medical Technologist":       (0.10, 65000, 100000),
    "Allied Health Professional": (0.10, 60000, 105000),
    "Administration":             (0.10, 45000, 85000),
    "Management":                 (0.05, 95000, 160000),
}
job_names = list(job_info.keys())
job_shares = [v[0] for v in job_info.values()]

rows = []
for i in range(1, NUM_MEMBERS + 1):
    job = rng.choice(job_names, p=job_shares)
    _, sal_min, sal_max = job_info[job]

    # Age today: most members are between 25 and 70
    age = int(np.clip(rng.normal(46, 11), 22, 75))
    birth_year = TODAY.year - age
    birth_date = date(birth_year, int(rng.integers(1, 13)), int(rng.integers(1, 29)))

    # People usually start working in healthcare between age 21 and 40
    start_age = int(rng.integers(21, 41))
    start_age = min(start_age, age - 1)
    hire_year = birth_year + start_age
    hire_date = date(hire_year, int(rng.integers(1, 13)), int(rng.integers(1, 29)))

    employment_type = rng.choice(["Full-Time", "Part-Time"], p=[0.75, 0.25])

    # ---- Did this member already retire? ----
    # Most people retire between 55 and 67. Some retire early.
    planned_retirement_age = int(np.clip(rng.normal(62, 3.5), 55, 70))
    # Managers and people with high salaries retire a little earlier on average
    if job == "Management":
        planned_retirement_age -= 1

    if age >= planned_retirement_age:
        status = "Retired"
        retirement_age = planned_retirement_age
        retirement_date = date(birth_year + retirement_age, birth_date.month, birth_date.day)
        last_work_year = retirement_date.year
    else:
        # Some active-age people left their job but kept their pension (Deferred)
        status = rng.choice(["Active", "Deferred"], p=[0.92, 0.08])
        retirement_age = None
        retirement_date = None
        last_work_year = TODAY.year

    years_of_service = round(max(last_work_year - hire_year, 0) *
                             (0.6 if employment_type == "Part-Time" else 1.0), 1)

    # Salary grows a bit with years of service
    base_salary = rng.uniform(sal_min, sal_max)
    salary = base_salary * (1 + min(years_of_service, 30) * 0.008)
    if employment_type == "Part-Time":
        salary *= 0.6
    salary = round(salary, -2)  # round to nearest 100

    # Members contribute about 9% of salary per year (simplified)
    annual_contribution = round(salary * 0.09, 2)

    rows.append({
        "member_id": f"M{i:05d}",
        "employer_id": rng.choice(employers_df["employer_id"]),
        "job_category": job,
        "employment_type": employment_type,
        "birth_date": birth_date,
        "hire_date": hire_date,
        "status": status,
        "retirement_date": retirement_date,
        "years_of_service": years_of_service,
        "annual_salary": salary,
        "annual_contribution": annual_contribution,
    })

members_df = pd.DataFrame(rows)

# ---------------------------------------------------------------------------
# 3. ADD A FEW REAL-WORLD DATA PROBLEMS ON PURPOSE
# ---------------------------------------------------------------------------
# Real data is never perfect. We add a few problems so that later we can
# show we know how to FIND and FIX them (data quality = data governance).
bad_rows = rng.choice(members_df.index, size=40, replace=False)
members_df.loc[bad_rows[:20], "annual_salary"] = None          # missing salary
members_df.loc[bad_rows[20:30], "job_category"] = "registered nurse"  # wrong spelling/case
members_df = pd.concat([members_df, members_df.loc[bad_rows[30:40]]])  # 10 duplicate rows

# ---------------------------------------------------------------------------
# 4. SAVE TO CSV FILES
# ---------------------------------------------------------------------------
employers_df.to_csv("data/employers.csv", index=False)
members_df.to_csv("data/members.csv", index=False)

print("Done!")
print(f"  employers.csv: {len(employers_df)} rows")
print(f"  members.csv:   {len(members_df)} rows")
print("\nMembers by status:")
print(members_df["status"].value_counts().to_string())
