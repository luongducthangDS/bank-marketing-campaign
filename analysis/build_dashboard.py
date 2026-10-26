"""Build Power BI star schema CSVs and an interactive Plotly HTML dashboard for Bank Marketing.

Outputs:
- powerbi/*.csv
- reports/dashboard.html
"""
from pathlib import Path
import duckdb
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parents[1]
PBI = ROOT / "powerbi"
REP = ROOT / "reports"
PBI.mkdir(parents=True, exist_ok=True)
REP.mkdir(parents=True, exist_ok=True)


def main():
    con = duckdb.connect()
    con.execute("SET enable_progress_bar = false")
    con.execute(f"SET file_search_path = '{ROOT}'")
    con.execute((ROOT / "sql" / "00_model.sql").read_text())
    con.execute((ROOT / "sql" / "10_powerbi_export.sql").read_text())

    # 1. Export Power BI CSVs
    pbi_tables = [
        ("pbi_fact_campaign_calls", "fact_campaign_calls.csv"),
        ("pbi_dim_client_profile", "dim_client_profile.csv"),
    ]
    for tbl, fname in pbi_tables:
        csv_path = (PBI / fname).as_posix()
        con.execute(f"COPY {tbl} TO '{csv_path}' (HEADER, DELIMITER ',')")
        print(f"Exported {tbl} -> {PBI / fname}")

    # 2. Build Interactive HTML Dashboard
    df_fatigue = con.execute("""
        SELECT
            campaign_contacts,
            count(*) AS contacts,
            round(avg(is_subscribed::INT) * 100, 2) AS conv_rate,
            round(sum(simulated_call_cost_eur), 2) AS labor_cost
        FROM fct_campaign_calls
        WHERE campaign_contacts <= 7
        GROUP BY campaign_contacts
        ORDER BY campaign_contacts
    """).fetchdf()

    df_macro = con.execute("""
        SELECT
            CASE
                WHEN euribor3m < 2.0 THEN '<2.0% (Low)'
                WHEN euribor3m <= 4.0 THEN '2.0-4.0% (Medium)'
                ELSE '>4.0% (High)'
            END AS euribor_band,
            round(avg(is_subscribed::INT) * 100, 2) AS conv_rate,
            count(*) AS contacts
        FROM fct_campaign_calls
        GROUP BY 1
        ORDER BY min(euribor3m) ASC
    """).fetchdf()

    df_channel = con.execute("""
        SELECT
            contact_type,
            round(avg(is_subscribed::INT) * 100, 2) AS conv_rate,
            count(*) AS contacts
        FROM fct_campaign_calls
        GROUP BY contact_type
    """).fetchdf()

    df_strike = con.execute("""
        SELECT
            CASE WHEN is_excess_call THEN 'Calls 4+ (Excess/Fatigue)' ELSE 'Calls 1-3 (Optimal)' END AS policy_group,
            count(*) AS total_contacts,
            count(CASE WHEN is_subscribed THEN 1 END) AS conversions,
            round(sum(simulated_call_cost_eur), 2) AS cost
        FROM fct_campaign_calls
        GROUP BY is_excess_call
        ORDER BY is_excess_call ASC
    """).fetchdf()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Diminishing Returns: Conversion Rate % by Call Sequence",
            "Macroeconomic Sensitivity: Conversion vs Euribor 3M Rate",
            "Channel Efficiency: Cellular vs Landline Telephone",
            "The 3-Strike Policy: Contact Volume vs Conversions"
        ),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "pie"}]]
    )

    # 1. Diminishing returns curve
    fig.add_trace(
        go.Bar(
            x=[f"Call {c}" for c in df_fatigue["campaign_contacts"]],
            y=df_fatigue["conv_rate"],
            text=df_fatigue["conv_rate"].apply(lambda x: f"{x}%"),
            textposition="auto",
            marker_color=["#10B981", "#3B82F6", "#6366F1", "#F59E0B", "#EF4444", "#DC2626", "#991B1B"],
            name="Conversion Rate %"
        ),
        row=1, col=1
    )

    # 2. Macro Sensitivity
    fig.add_trace(
        go.Bar(
            x=df_macro["euribor_band"],
            y=df_macro["conv_rate"],
            text=df_macro["conv_rate"].apply(lambda x: f"{x}%"),
            textposition="auto",
            marker_color="#8B5CF6",
            name="Euribor Rate %"
        ),
        row=1, col=2
    )

    # 3. Channel Efficiency
    fig.add_trace(
        go.Bar(
            x=df_channel["contact_type"],
            y=df_channel["conv_rate"],
            text=df_channel["conv_rate"].apply(lambda x: f"{x}%"),
            textposition="auto",
            marker_color=["#06B6D4", "#F43F5E"],
            name="Channel Conv %"
        ),
        row=2, col=1
    )

    # 4. Strike Policy Pie
    fig.add_trace(
        go.Pie(
            labels=df_strike["policy_group"],
            values=df_strike["conversions"],
            hole=0.45,
            marker_colors=["#10B981", "#EF4444"],
            name="Conversions"
        ),
        row=2, col=2
    )

    fig.update_layout(
        title_text="<b>Bank Marketing Campaign & ROI Optimization Dashboard</b><br><sup>Diminishing Returns, Contact Frequency Capping, and Macroeconomic Sensitivity</sup>",
        template="plotly_white",
        height=850,
        showlegend=False
    )

    dashboard_path = REP / "dashboard.html"
    fig.write_html(str(dashboard_path), include_plotlyjs="cdn")
    print(f"Generated interactive dashboard: {dashboard_path}")


if __name__ == "__main__":
    main()
