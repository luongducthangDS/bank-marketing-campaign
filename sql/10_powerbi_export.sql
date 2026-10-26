-- Power BI Star Schema Export for Bank Marketing

CREATE OR REPLACE TABLE pbi_dim_client_profile AS
SELECT DISTINCT
    md5(job || '|' || marital || '|' || education || '|' || credit_default || '|' ||
        CAST(has_housing_loan AS VARCHAR) || '|' || CAST(has_personal_loan AS VARCHAR) || '|' || age_group) AS profile_id,
    job,
    marital,
    education,
    credit_default,
    has_housing_loan,
    has_personal_loan,
    age_group
FROM fct_campaign_calls;

CREATE OR REPLACE TABLE pbi_fact_campaign_calls AS
SELECT
    c.call_id,
    md5(c.job || '|' || c.marital || '|' || c.education || '|' || c.credit_default || '|' ||
        CAST(c.has_housing_loan AS VARCHAR) || '|' || CAST(c.has_personal_loan AS VARCHAR) || '|' || c.age_group) AS profile_id,
    c.age,
    c.contact_type,
    c.call_month,
    c.call_day_of_week,
    c.campaign_contacts,
    c.contact_frequency_tier,
    c.is_excess_call,
    c.pdays,
    c.was_previously_contacted,
    c.previous_campaign_contacts,
    c.previous_outcome,
    c.emp_var_rate,
    c.cons_price_idx,
    c.cons_conf_idx,
    c.euribor3m,
    c.nr_employed,
    c.duration_seconds,
    c.simulated_call_cost_eur,
    c.simulated_revenue_eur,
    c.is_subscribed
FROM fct_campaign_calls c;
