"""Generate publication-quality figures for Bank Marketing analytics README."""
from pathlib import Path
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

INK, MUTED, GRID = "#1F2937", "#6B7280", "#E5E7EB"
BLUE, RED, GREEN, AMBER, PURPLE = "#2563EB", "#DC2626", "#059669", "#D97706", "#7C3AED"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.titlelocation": "left",
    "axes.titleweight": "bold",
    "axes.titlecolor": INK
})


def generate():
    con = duckdb.connect()
    con.execute("SET enable_progress_bar = false")
    con.execute(f"SET file_search_path = '{ROOT}'")
    con.execute((ROOT / "sql" / "00_model.sql").read_text())

    fig, axes = plt.subplots(2, 2, figsize=(14, 9), dpi=150)
    fig.patch.set_facecolor("#FAFAFA")
    for ax in axes.flat:
        ax.set_facecolor("white")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color=GRID, linestyle="--", alpha=0.7)
        ax.set_axisbelow(True)

    # 1. Diminishing Returns by Call Frequency
    fatigue = con.execute("""
        SELECT campaign_contacts, round(avg(is_subscribed::INT)*100, 1) AS conv_rate, count(*) AS calls
        FROM fct_campaign_calls
        WHERE campaign_contacts <= 7
        GROUP BY campaign_contacts
        ORDER BY campaign_contacts
    """).fetchall()
    x1 = [f"Call {f[0]}" if f[0] < 7 else "Call 7+" for f in fatigue]
    y1 = [f[1] for f in fatigue]
    c1 = [GREEN, BLUE, BLUE, AMBER, RED, RED, RED]
    bars1 = axes[0, 0].bar(x1, y1, color=c1, width=0.55, zorder=3)
    axes[0, 0].set_title("A. Diminishing Returns: Conversion % by Call Sequence")
    axes[0, 0].set_ylabel("Conversion Rate (%)")
    axes[0, 0].set_ylim(0, max(y1) * 1.25)
    for b in bars1:
        axes[0, 0].text(b.get_x() + b.get_width() / 2, b.get_height() + 0.4,
                        f"{b.get_height():.1f}%", ha="center", va="bottom", fontweight="bold", color=INK)

    # 2. 3-Strike Policy Efficiency
    strike = con.execute("""
        SELECT
            CASE WHEN is_excess_call THEN 'Calls 4+\n(Excess/Fatigue)' ELSE 'Calls 1–3\n(Recommended Cap)' END AS grp,
            count(*) AS total_dials,
            count(CASE WHEN is_subscribed THEN 1 END) AS conversions,
            round(sum(simulated_call_cost_eur)/1000, 1) AS labor_cost_k
        FROM fct_campaign_calls
        GROUP BY is_excess_call
        ORDER BY is_excess_call ASC
    """).fetchall()
    x2 = [s[0] for s in strike]
    y2_conv = [s[2] for s in strike]
    tot_conv = sum(y2_conv)
    c2 = [GREEN, RED]
    bars2 = axes[0, 1].bar(x2, y2_conv, color=c2, width=0.45, zorder=3)
    axes[0, 1].set_title("B. The 3-Strike Policy: 88% Conversions in First 3 Calls")
    axes[0, 1].set_ylabel("Total Deposit Conversions")
    axes[0, 1].set_ylim(0, max(y2_conv) * 1.25)
    for b, s in zip(bars2, strike):
        pct = (b.get_height() / tot_conv) * 100
        axes[0, 1].text(b.get_x() + b.get_width() / 2, b.get_height() + 80,
                        f"{b.get_height():,}\n({pct:.1f}% of total)\nCost: €{s[3]:.1f}k",
                        ha="center", va="bottom", fontsize=9, fontweight="bold", color=INK)

    # 3. Macroeconomic Sensitivity (Euribor 3M)
    macro = con.execute("""
        SELECT
            CASE
                WHEN euribor3m < 2.0 THEN 'Low (<2.0%)\nStimulus'
                WHEN euribor3m <= 4.0 THEN 'Medium (2–4%)\nNeutral'
                ELSE 'High (>4.0%)\nTightening'
            END AS euribor_band,
            round(avg(is_subscribed::INT)*100, 1) AS conv_rate,
            count(*) AS dials
        FROM fct_campaign_calls
        GROUP BY 1
        ORDER BY min(euribor3m) ASC
    """).fetchall()
    x3 = [m[0] for m in macro]
    y3 = [m[1] for m in macro]
    c3 = [GREEN, AMBER, RED]
    bars3 = axes[1, 0].bar(x3, y3, color=c3, width=0.55, zorder=3)
    axes[1, 0].set_title("C. Macro Environment: Conversion vs Euribor 3M Rate")
    axes[1, 0].set_ylabel("Conversion Rate (%)")
    axes[1, 0].set_ylim(0, max(y3) * 1.25)
    for b in bars3:
        axes[1, 0].text(b.get_x() + b.get_width() / 2, b.get_height() + 0.6,
                        f"{b.get_height():.1f}%", ha="center", va="bottom", fontweight="bold", color=INK)

    # 4. Channel & Prior Experience Lift
    channel = con.execute("""
        SELECT
            contact_type,
            round(avg(is_subscribed::INT)*100, 1) AS conv_rate
        FROM fct_campaign_calls
        GROUP BY contact_type
    """).fetchall()
    prev_lift = con.execute("""
        SELECT
            CASE WHEN previous_outcome = 'success' THEN 'Prior Campaign\nSuccess' ELSE 'Cold / First Contact' END,
            round(avg(is_subscribed::INT)*100, 1) AS conv_rate
        FROM fct_campaign_calls
        GROUP BY 1
        ORDER BY conv_rate ASC
    """).fetchall()
    combo = [("Landline", channel[1][1], RED),
             ("Cellular Mobile", channel[0][1], BLUE),
             ("Cold Lead", prev_lift[0][1], AMBER),
             ("Prior Success Lead", prev_lift[1][1], GREEN)]
    x4 = [c[0] for c in combo]
    y4 = [c[1] for c in combo]
    c4 = [c[2] for c in combo]
    bars4 = axes[1, 1].bar(x4, y4, color=c4, width=0.55, zorder=3)
    axes[1, 1].set_title("D. Channel & Lead History Response Rate")
    axes[1, 1].set_ylabel("Conversion Rate (%)")
    axes[1, 1].set_ylim(0, max(y4) * 1.25)
    axes[1, 1].tick_params(axis="x", rotation=15)
    for b in bars4:
        axes[1, 1].text(b.get_x() + b.get_width() / 2, b.get_height() + 1.2,
                        f"{b.get_height():.1f}%", ha="center", va="bottom", fontweight="bold", color=INK)

    fig.suptitle("BANK MARKETING TELEMARKETING PERFORMANCE & ROI DASHBOARD",
                 fontsize=14, fontweight="bold", y=0.98, color=INK)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out = FIG / "00_dashboard_preview.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Generated {out}")


if __name__ == "__main__":
    generate()
