// Power Query M script for loading Bank Marketing Star Schema CSVs
let
    SourceDir = "D:\github\go to offer\data-analyst\bank-marketing-campaign\powerbi\",
    LoadFact = Csv.Document(File.Contents(SourceDir & "fact_campaign_calls.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedFact = Table.PromoteHeaders(LoadFact, [PromoteAllScalars=true]),
    TypedFact = Table.TransformColumnTypes(PromotedFact, {
        {"call_id", Int64.Type},
        {"profile_id", type text},
        {"age", Int64.Type},
        {"contact_type", type text},
        {"call_month", type text},
        {"call_day_of_week", type text},
        {"campaign_contacts", Int64.Type},
        {"contact_frequency_tier", type text},
        {"is_excess_call", type logical},
        {"pdays", Int64.Type},
        {"was_previously_contacted", type logical},
        {"previous_campaign_contacts", Int64.Type},
        {"previous_outcome", type text},
        {"emp_var_rate", type number},
        {"cons_price_idx", type number},
        {"cons_conf_idx", type number},
        {"euribor3m", type number},
        {"nr_employed", type number},
        {"duration_seconds", Int64.Type},
        {"simulated_call_cost_eur", type number},
        {"simulated_revenue_eur", type number},
        {"is_subscribed", type logical}
    })
in
    TypedFact
