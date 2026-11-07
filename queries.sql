-- =====================================================================
-- queries.sql
-- Pension Member Insights: business questions answered with SQL
-- Data is "as of" 2026-10-01
-- =====================================================================


-- ---------------------------------------------------------------------
-- Q1. OVERVIEW: How many members do we have in each status?
--     (Active = working now, Retired = getting a pension,
--      Deferred = left the job but will get a pension later)
-- ---------------------------------------------------------------------
SELECT
    status,
    COUNT(*)                                   AS members,
    ROUND(AVG((julianday('2026-10-01') - julianday(birth_date)) / 365.25), 1) AS avg_age,
    ROUND(AVG(annual_salary), 0)               AS avg_salary
FROM members
GROUP BY status
ORDER BY members DESC;


-- ---------------------------------------------------------------------
-- Q2. At what age do members usually retire? (by job category)
--     We look only at members who already retired.
-- ---------------------------------------------------------------------
SELECT
    job_category,
    COUNT(*) AS retired_members,
    ROUND(AVG((julianday(retirement_date) - julianday(birth_date)) / 365.25), 1) AS avg_retirement_age
FROM members
WHERE status = 'Retired'
GROUP BY job_category
ORDER BY avg_retirement_age;


-- ---------------------------------------------------------------------
-- Q3. RETIREMENT WAVE: How many ACTIVE members will reach age 60
--     (the typical retirement age we found in Q2) in the next 5 and 10 years?
--     This helps the plan prepare: more retirees = more pensions to pay.
-- ---------------------------------------------------------------------
WITH active_ages AS (
    SELECT
        job_category,
        (julianday('2026-10-01') - julianday(birth_date)) / 365.25 AS age
    FROM members
    WHERE status = 'Active'
)
SELECT
    job_category,
    COUNT(*)                                        AS active_members,
    SUM(CASE WHEN age >= 55 THEN 1 ELSE 0 END)      AS retiring_in_5_years,
    SUM(CASE WHEN age >= 50 THEN 1 ELSE 0 END)      AS retiring_in_10_years,
    ROUND(100.0 * SUM(CASE WHEN age >= 50 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                    AS pct_retiring_in_10_years
FROM active_ages
GROUP BY job_category
ORDER BY pct_retiring_in_10_years DESC;


-- ---------------------------------------------------------------------
-- Q4. Which employers have the OLDEST workforce?
--     Top 10 employers by % of active members aged 55 or older.
--     (Uses a JOIN to get the employer name and region.)
-- ---------------------------------------------------------------------
SELECT
    e.employer_name,
    e.region,
    COUNT(*) AS active_members,
    ROUND(100.0 * SUM(CASE WHEN (julianday('2026-10-01') - julianday(m.birth_date)) / 365.25 >= 55
                           THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_age_55_plus
FROM members m
JOIN employers e ON m.employer_id = e.employer_id
WHERE m.status = 'Active'
GROUP BY e.employer_name, e.region
ORDER BY pct_age_55_plus DESC
LIMIT 10;


-- ---------------------------------------------------------------------
-- Q5. How do contributions change by AGE GROUP? (active members only)
-- ---------------------------------------------------------------------
WITH grouped AS (
    SELECT
        CASE
            WHEN (julianday('2026-10-01') - julianday(birth_date)) / 365.25 < 30 THEN '1. Under 30'
            WHEN (julianday('2026-10-01') - julianday(birth_date)) / 365.25 < 40 THEN '2. 30-39'
            WHEN (julianday('2026-10-01') - julianday(birth_date)) / 365.25 < 50 THEN '3. 40-49'
            WHEN (julianday('2026-10-01') - julianday(birth_date)) / 365.25 < 60 THEN '4. 50-59'
            ELSE '5. 60+'
        END AS age_group,
        annual_contribution
    FROM members
    WHERE status = 'Active'
)
SELECT
    age_group,
    COUNT(*)                            AS members,
    ROUND(AVG(annual_contribution), 0)  AS avg_contribution,
    ROUND(SUM(annual_contribution), 0)  AS total_contribution
FROM grouped
GROUP BY age_group
ORDER BY age_group;
