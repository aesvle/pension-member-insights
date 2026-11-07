# Pension Member Insights Dashboard

An end-to-end analytics project about the members of a healthcare pension plan in Ontario. It answers one big question:

**How many members will retire soon, and where should the plan prepare?**

> Note: all data in this project is **synthetic** (generated with Python). Real pension member data is private.

![Dashboard](dashboard.png)

## Tools
Python (pandas, NumPy, scikit-learn) · SQL (SQLite) · Power BI

## Key findings
- Members retire at about **age 60** on average.
- **29% of active members** (1,219 people) will reach typical retirement age in the next 10 years.
- **Administration (34%)** and **Registered Practical Nurses (32%)** have the highest share of members close to retirement.
- The retirement risk is similar across employer types (27% to 30%), so the plan needs to prepare everywhere, not only in one area.
- The 2 individual employers with the oldest workforce are both **long-term care** homes.
- The machine learning model flags **44 active members** with a high chance of retiring soon.

## Project steps
| Step | File | What it does |
|---|---|---|
| 1 | `generate_data.py` | Creates 5,000 realistic pension members and 25 employers, with some data quality problems on purpose |
| 2 | `load_to_sql.py` | Cleans the data (duplicates, inconsistent text, missing values) and loads it into a SQL database |
| 3 | `queries.sql` + `run_queries.py` | Answers 5 business questions with SQL (CTEs, JOINs, CASE, aggregations) |
| 4 | `export_for_powerbi.py` + `pension_dashboard.pbix` | Adds age groups and retirement windows in SQL, then builds an interactive Power BI dashboard |
| 5 | `retirement_model.py` | Logistic Regression model that gives each active member aged 50+ a retirement risk score (83% accuracy on test data) |
| 6 | `DATA_DICTIONARY.md` | Explains every table and column |

## The machine learning model (simple version)
- **Learns from:** members aged 55+, some retired and some still working
- **Uses:** age, job category, full-time or part-time
- **Predicts:** how much an active member "looks like" someone who already retired
- **Result:** 83% correct on members it never saw during training
- `years_of_service` was left out on purpose: for retired members it stops growing at retirement, so it would leak the answer to the model (data leakage).

## How to run
```bash
pip install -r requirements.txt
python generate_data.py
python load_to_sql.py
python run_queries.py
python export_for_powerbi.py
python retirement_model.py
```
Then open `pension_dashboard.pbix` in Power BI Desktop.
