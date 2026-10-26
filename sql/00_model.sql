-- Bank Marketing Campaign Performance & Call Fatigue Model
-- Built in DuckDB from data/raw/bank_marketing_raw.csv (delim=';')

CREATE OR REPLACE TABLE raw_bank AS
SELECT * FROM read_csv('data/raw/bank_marketing_raw.csv', delim=';', header=true, all_varchar=true);

CREATE OR REPLACE TABLE fct_campaign_calls AS
SELECT
    row_number() OVER ()                                                AS call_id,
    CAST("age" AS INTEGER)                                              AS age,
    CASE
        WHEN CAST("age" AS INTEGER) < 30 THEN '<30 Young'
        WHEN CAST("age" AS INTEGER) <= 39 THEN '30-39 Young Adult'
        WHEN CAST("age" AS INTEGER) <= 49 THEN '40-49 Middle Age'
        WHEN CAST("age" AS INTEGER) <= 59 THEN '50-59 Mature'
        ELSE '60+ Senior'
    END                                                                 AS age_group,
    TRIM("job")                                                         AS job,
    TRIM("marital")                                                     AS marital,
    TRIM("education")                                                   AS education,
    TRIM("default")                                                     AS credit_default,
    TRIM("housing") = 'yes'                                             AS has_housing_loan,
    TRIM("loan") = 'yes'                                                AS has_personal_loan,
    TRIM("contact")                                                     AS contact_type,
    TRIM("month")                                                       AS call_month,
    TRIM("day_of_week")                                                 AS call_day_of_week,
    CAST("duration" AS INTEGER)                                         AS duration_seconds,
    CAST("campaign" AS INTEGER)                                         AS campaign_contacts,
    CASE
        WHEN CAST("campaign" AS INTEGER) = 1 THEN '1 call'
        WHEN CAST("campaign" AS INTEGER) = 2 THEN '2 calls'
        WHEN CAST("campaign" AS INTEGER) = 3 THEN '3 calls'
        WHEN CAST("campaign" AS INTEGER) <= 6 THEN '4-6 calls'
        ELSE '>6 calls (Excess/Fatigue)'
    END                                                                 AS contact_frequency_tier,
    CAST("campaign" AS INTEGER) > 3                                     AS is_excess_call,
    CAST("pdays" AS INTEGER)                                            AS pdays,
    CAST("pdays" AS INTEGER) <> 999                                     AS was_previously_contacted,
    CAST("previous" AS INTEGER)                                         AS previous_campaign_contacts,
    TRIM("poutcome")                                                    AS previous_outcome,
    CAST("emp.var.rate" AS DOUBLE)                                      AS emp_var_rate,
    CAST("cons.price.idx" AS DOUBLE)                                    AS cons_price_idx,
    CAST("cons.conf.idx" AS DOUBLE)                                     AS cons_conf_idx,
    CAST("euribor3m" AS DOUBLE)                                         AS euribor3m,
    CAST("nr.employed" AS DOUBLE)                                       AS nr_employed,
    TRIM("y") = 'yes'                                                   AS is_subscribed,
    -- Financial ROI Simulation Metrics:
    -- Estimated labor cost: €1.00 dial cost + €0.50 per minute of duration
    ROUND(1.00 + (CAST("duration" AS INTEGER) / 60.0) * 0.50, 2)       AS simulated_call_cost_eur,
    -- Estimated lifetime value generated: €120 profit per converted term deposit
    CASE WHEN TRIM("y") = 'yes' THEN 120.00 ELSE 0.00 END               AS simulated_revenue_eur
FROM raw_bank;
