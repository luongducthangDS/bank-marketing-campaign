# Power BI Rebuild Guide: Bank Marketing Campaign Performance & ROI

This directory contains star schema CSVs generated from `sql/10_powerbi_export.sql` via `python analysis/build_dashboard.py`.

## Data Model & Relationships

1. Load the 2 CSV files:
   - `fact_campaign_calls.csv` (41,188 rows of telemarketing contacts)
   - `dim_client_profile.csv` (Distinct demographic profiles: job, education, marital, loans)

2. Create 1-to-many relationships (Single direction filter):
   - `dim_client_profile[profile_id]` 1 ---> * `fact_campaign_calls[profile_id]`

3. Create DAX measures from `measures.dax`.
