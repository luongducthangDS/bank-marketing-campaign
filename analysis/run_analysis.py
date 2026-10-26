"""Statistical and ROI simulation analysis for UCI Bank Marketing telemarketing campaign.

Outputs:
- reports/results.json (reproducible metrics quoted in decision memo & README)
"""
import json
from pathlib import Path
import duckdb
import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "reports"
REP.mkdir(parents=True, exist_ok=True)


def load_model():
    con = duckdb.connect()
    con.execute("SET enable_progress_bar = false")
    con.execute(f"SET file_search_path = '{ROOT}'")
    con.execute((ROOT / "sql" / "00_model.sql").read_text())
    con.execute((ROOT / "sql" / "10_powerbi_export.sql").read_text())
    return con


def run():
    con = load_model()

    # 1. Headline KPIs
    kpi_query = """
    SELECT
        count(*)                                                    AS total_contacts,
        count(CASE WHEN is_subscribed THEN 1 END)                   AS total_subscriptions,
        round(avg(is_subscribed::INT) * 100, 2)                     AS conversion_rate_pct,
        round(sum(simulated_call_cost_eur), 2)                      AS total_labor_cost_eur,
        round(sum(simulated_revenue_eur), 2)                        AS total_gross_value_eur,
        round(sum(simulated_revenue_eur) - sum(simulated_call_cost_eur), 2) AS simulated_net_profit_eur,
        round((sum(simulated_revenue_eur) - sum(simulated_call_cost_eur)) / sum(simulated_call_cost_eur) * 100, 1) AS simulated_roi_pct
    FROM fct_campaign_calls;
    """
    kpis = con.execute(kpi_query).fetchdf().to_dict(orient="records")[0]

    # 2. Diminishing Returns by Call Frequency (Calls 1 to 10+)
    fatigue_query = """
    SELECT
        campaign_contacts,
        count(*)                                                    AS contacts_count,
        count(CASE WHEN is_subscribed THEN 1 END)                   AS subscriptions,
        round(avg(is_subscribed::INT) * 100, 2)                     AS conversion_rate_pct,
        round(sum(simulated_call_cost_eur), 2)                      AS labor_cost_eur
    FROM fct_campaign_calls
    WHERE campaign_contacts <= 7
    GROUP BY campaign_contacts
    ORDER BY campaign_contacts;
    """
    call_fatigue = con.execute(fatigue_query).fetchdf().to_dict(orient="records")

    # 3. 3-Strike Policy Benchmark (Calls <= 3 vs Calls > 3)
    policy_query = """
    SELECT
        is_excess_call,
        count(*)                                                    AS contacts_count,
        round(count(*) * 100.0 / (SELECT count(*) FROM fct_campaign_calls), 2) AS contacts_share_pct,
        count(CASE WHEN is_subscribed THEN 1 END)                   AS subscriptions,
        round(count(CASE WHEN is_subscribed THEN 1 END) * 100.0 / (SELECT count(CASE WHEN is_subscribed THEN 1 END) FROM fct_campaign_calls), 2) AS subscriptions_share_pct,
        round(avg(is_subscribed::INT) * 100, 2)                     AS conversion_rate_pct,
        round(sum(simulated_call_cost_eur), 2)                      AS total_labor_cost_eur
    FROM fct_campaign_calls
    GROUP BY is_excess_call
    ORDER BY is_excess_call ASC;
    """
    strike_policy = con.execute(policy_query).fetchdf().to_dict(orient="records")

    # 4. Macroeconomic Impact (Euribor 3M rate)
    macro_query = """
    SELECT
        CASE
            WHEN euribor3m < 2.0 THEN 'Low (<2.0% Stimulus)'
            WHEN euribor3m <= 4.0 THEN 'Moderate (2.0 - 4.0%)'
            ELSE 'High (>4.0% Tightening)'
        END AS euribor_environment,
        count(*)                                                    AS contacts_count,
        count(CASE WHEN is_subscribed THEN 1 END)                   AS subscriptions,
        round(avg(is_subscribed::INT) * 100, 2)                     AS conversion_rate_pct
    FROM fct_campaign_calls
    GROUP BY 1
    ORDER BY min(euribor3m) ASC;
    """
    macro_trends = con.execute(macro_query).fetchdf().to_dict(orient="records")

    # 5. Logistic Regression for Odds Ratios (Data Leakage Free: NO duration)
    # Features: campaign_contacts, is_cellular, was_previously_contacted, previous_success, euribor3m
    model_data = con.execute("""
        SELECT
            is_subscribed::INT,
            campaign_contacts,
            (contact_type = 'cellular')::INT,
            was_previously_contacted::INT,
            (previous_outcome = 'success')::INT,
            euribor3m
        FROM fct_campaign_calls
    """).fetchall()

    y = np.array([r[0] for r in model_data])
    X = np.column_stack([
        np.ones(len(model_data)),
        [r[1] for r in model_data],  # campaign contacts
        [r[2] for r in model_data],  # is cellular
        [r[3] for r in model_data],  # previously contacted
        [r[4] for r in model_data],  # previous success
        [r[5] for r in model_data],  # euribor3m
    ])

    feature_names = ["Intercept", "Campaign Contacts Count", "Cellular Contact", "Previously Contacted", "Previous Campaign Success", "Euribor 3M Rate"]

    def neg_log_lik(beta):
        logits = np.clip(X @ beta, -30, 30)
        p = 1.0 / (1.0 + np.exp(-logits))
        eps = 1e-15
        p = np.clip(p, eps, 1.0 - eps)
        return -np.sum(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))

    res = minimize(neg_log_lik, np.zeros(X.shape[1]), method="BFGS")
    beta = res.x
    logits = np.clip(X @ beta, -30, 30)
    p = 1.0 / (1.0 + np.exp(-logits))
    W = p * (1.0 - p)
    info_matrix = X.T @ (X * W[:, None])
    vcov = np.linalg.pinv(info_matrix)
    se = np.sqrt(np.diag(vcov))

    odds_ratios = []
    for i in range(1, len(feature_names)):
        coef = beta[i]
        odds = np.exp(coef)
        ci_low = np.exp(coef - 1.96 * se[i])
        ci_high = np.exp(coef + 1.96 * se[i])
        odds_ratios.append({
            "feature": feature_names[i],
            "odds_ratio": round(float(odds), 3),
            "ci_95_pct": [round(float(ci_low), 3), round(float(ci_high), 3)],
            "interpretation": "Boosts conversion" if odds > 1.0 else "Decreases conversion"
        })

    results = {
        "kpis": kpis,
        "call_fatigue_curve": call_fatigue,
        "three_strike_policy_comparison": strike_policy,
        "macro_environment": macro_trends,
        "leakage_free_odds_ratios": odds_ratios
    }

    out_file = REP / "results.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Bank Marketing analysis completed! Saved to {out_file}")
    print("\n--- Headline Findings ---")
    print(f"Total Contacts: {kpis['total_contacts']:,} | Conversion Rate: {kpis['conversion_rate_pct']}%")
    print(f"Simulated Labor Cost: €{kpis['total_labor_cost_eur']:,.2f} | Net Value: €{kpis['simulated_net_profit_eur']:,.2f}")
    print(f"Calls <=3 hold {strike_policy[0]['subscriptions_share_pct']}% of conversions while using only {strike_policy[0]['contacts_share_pct']}% of contacts!")
    print(f"Previous Campaign Success Odds Ratio: {odds_ratios[3]['odds_ratio']}x higher conversion!")


if __name__ == "__main__":
    run()
