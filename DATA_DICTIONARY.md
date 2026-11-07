# Data Dictionary

This file explains every table and column in the Pension Member Insights project.
All data is **synthetic** (made with Python). The "as of" date is **2026-10-01**.

---

## Table: `employers`
25 healthcare employers in Ontario. One row = one employer.

| Column | Type | Description | Example |
|---|---|---|---|
| employer_id | Text | Unique ID of the employer (primary key) | E001 |
| employer_name | Text | Name of the employer | Toronto Hospital 01 |
| employer_type | Text | Hospital, Long-Term Care, or Community Health | Hospital |
| region | Text | Ontario region: Toronto, Central, East, West, North | Toronto |

---

## Table: `members`
5,000 pension plan members (after cleaning). One row = one member.

| Column | Type | Description | Example |
|---|---|---|---|
| member_id | Text | Unique ID of the member (primary key) | M00001 |
| employer_id | Text | Employer of the member. Links to `employers.employer_id` | E014 |
| job_category | Text | Job group (7 categories, e.g. Registered Nurse, Management) | Registered Nurse |
| employment_type | Text | Full-Time or Part-Time | Full-Time |
| birth_date | Date | Date of birth | 1978-04-12 |
| hire_date | Date | Date the member started working in the plan | 2005-09-03 |
| status | Text | Active (working now), Retired (receiving a pension), Deferred (left the job, pension later) | Active |
| retirement_date | Date | Date of retirement. Empty if not retired | 2024-06-15 |
| years_of_service | Number | Years in the plan. Part-time years count as 0.6. Stops growing at retirement | 21.0 |
| annual_salary | Number (CAD) | Yearly salary. 20 missing values were filled with the median for the same job and employment type | 92400 |
| annual_contribution | Number (CAD) | Yearly amount the member pays into the plan (about 9% of salary) | 8316.00 |

---

## Extra columns in `powerbi/members_clean.csv`
Created by `export_for_powerbi.py`. Same rows as `members`, plus these columns:

| Column | Type | Description | Example |
|---|---|---|---|
| age | Number | Age on 2026-10-01 | 48.5 |
| age_group | Text | Under 30, 30-39, 40-49, 50-59, 60+ | 3. 40-49 |
| years_to_retirement | Number | Years until age 60 (the typical retirement age). Only for Active members. 0 if already 60+ | 11.5 |
| retirement_window | Text | Eligible now, Within 5 years, In 5 to 10 years, More than 10 years, or Not active | 2. Within 5 years |

---

## File: `powerbi/retirement_risk.csv`
Created by `retirement_model.py`. One row = one Active member aged 50+.

| Column | Type | Description | Example |
|---|---|---|---|
| member_id | Text | Links to `members.member_id` | M02156 |
| age | Number | Age on 2026-10-01 | 67.9 |
| job_category | Text | Job group | Medical Technologist |
| retirement_risk | Number (0 to 1) | Model's probability that this member looks like someone who already retired | 0.96 |
| risk_level | Text | High (0.6 or more), Medium (0.3 to 0.6), Low (under 0.3) | High |

---

## Data quality fixes (in `load_to_sql.py`)
| Problem | How many | Fix |
|---|---|---|
| Duplicate rows | 10 | Removed |
| Wrong capitalization ("registered nurse") | 10 | Changed to Title Case |
| Missing salary | 20 | Filled with median salary for the same job and employment type |
