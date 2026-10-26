"""Generate publication-quality figures for Bank Marketing analytics README.
Generates:
- 00_dashboard_preview.png (Composite 4-panel executive overview, zero collision)
- 01_call_sequence_diminishing_returns.png (Standalone: Diminishing returns curve)
- 02_3strike_efficiency_comparison.png (Standalone: 3-Strike Policy resource comparison)
- 03_macro_euribor_conversion_drop.png (Standalone: Macro interest rate elasticity)
"""
from pathlib import Path
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

INK, MUTED, GRID = "#111827", "#4B5563", "#E5E7EB"
BLUE, RED, GREEN, AMBER, PURPLE = "#1D4ED8", "#DC2626", "#059669", "#D97706", "#7C3AED"

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

    # =========================================================================
    # 1. COMPOSITE DASHBOARD PREVIEW (00_dashboard_preview.png)
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(15, 9.8), dpi=160)
    fig.patch.set_facecolor("#FAFAFA")
    for ax in axes.flat:
        ax.set_facecolor("white")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color=GRID, linestyle="--", alpha=0.7)
        ax.set_axisbelow(True)

    # Panel A: Diminishing Returns by Call Frequency
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
    bars1 = axes[0, 0].bar(x1, y1, color=c1, width=0.52, zorder=3)
    axes[0, 0].set_title("A. Diminishing Returns: Conversion % by Call Sequence")
    axes[0, 0].set_ylabel("Conversion Rate (%)")
    axes[0, 0].set_ylim(0, 16)
    for b in bars1:
        h = b.get_height()
        axes[0, 0].text(b.get_x() + b.get_width() / 2, h + 0.4,
                        f"{h:.1f}%", ha="center", va="bottom",
                        fontweight="bold", fontsize=9, color=INK)

    # Panel B: 3-Strike Policy Efficiency
    strike = con.execute("""
        SELECT
            CASE WHEN is_excess_call THEN 'Calls 4+\n(Excess Fatigue)' ELSE 'Calls 1–3\n(Recommended Cap)' END AS grp,
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
    axes[0, 1].set_ylim(0, max(y2_conv) * 1.30)
    for b, s in zip(bars2, strike):
        pct = (b.get_height() / tot_conv) * 100
        axes[0, 1].text(b.get_x() + b.get_width() / 2, b.get_height() + 90,
                        f"{b.get_height():,} ({pct:.1f}%)\nCost: €{s[3]:.1f}k",
                        ha="center", va="bottom", fontsize=9, fontweight="bold", color=INK)

    # Panel C: Macroeconomic Sensitivity (Euribor 3M)
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
    bars3 = axes[1, 0].bar(x3, y3, color=c3, width=0.52, zorder=3)
    axes[1, 0].set_title("C. Macro Environment: Conversion vs Euribor 3M Rate")
    axes[1, 0].set_ylabel("Conversion Rate (%)")
    axes[1, 0].set_ylim(0, 28)
    for b in bars3:
        h = b.get_height()
        axes[1, 0].text(b.get_x() + b.get_width() / 2, h + 0.7,
                        f"{h:.1f}%", ha="center", va="bottom",
                        fontweight="bold", fontsize=9.5, color=INK)

    # Panel D: Channel & Lead Quality Lift (Horizontal barh eliminates label collision!)
    axes[1, 1].grid(axis="x", color=GRID, linestyle="--", alpha=0.7)
    channel = con.execute("""
        SELECT contact_type, round(avg(is_subscribed::INT)*100, 1) AS conv_rate
        FROM fct_campaign_calls
        GROUP BY contact_type
    """).fetchall()
    prev_lift = con.execute("""
        SELECT
            CASE WHEN previous_outcome = 'success' THEN 'Prior Success Lead' ELSE 'Cold / First Lead' END,
            round(avg(is_subscribed::INT)*100, 1) AS conv_rate
        FROM fct_campaign_calls
        GROUP BY 1
        ORDER BY conv_rate ASC
    """).fetchall()

    combo = [("Landline Phone", channel[1][1], RED),
             ("Cold Lead", prev_lift[0][1], AMBER),
             ("Cellular Mobile", channel[0][1], BLUE),
             ("Prior Success Lead", prev_lift[1][1], GREEN)]
    y4_names = [c[0] for c in combo]
    x4_vals = [c[1] for c in combo]
    c4 = [c[2] for c in combo]
    bars4 = axes[1, 1].barh(y4_names, x4_vals, color=c4, height=0.52, zorder=3)
    axes[1, 1].set_title("D. Channel & Past Lead Response Rate")
    axes[1, 1].set_xlabel("Conversion Rate (%)")
    axes[1, 1].set_xlim(0, max(x4_vals) * 1.30)
    for b in bars4:
        w = b.get_width()
        axes[1, 1].text(w + 1.2, b.get_y() + b.get_height() / 2,
                        f"{w:.1f}%", va="center", ha="left",
                        fontsize=9, fontweight="bold", color=INK)

    fig.suptitle("BANK MARKETING TELEMARKETING PERFORMANCE & ROI DASHBOARD",
                 fontsize=14, fontweight="bold", y=0.98, color=INK)
    fig.subplots_adjust(top=0.93, bottom=0.08, left=0.10, right=0.96, hspace=0.32, wspace=0.28)
    out0 = FIG / "00_dashboard_preview.png"
    fig.savefig(out0, dpi=160)
    plt.close(fig)
    print(f"Generated {out0}")

    # =========================================================================
    # 2. STANDALONE FIGURE 1: CALL SEQUENCE DIMINISHING RETURNS (01_call_sequence_diminishing_returns.png)
    # =========================================================================
    fig1, ax1 = plt.subplots(figsize=(10, 5.5), dpi=160)
    fig1.patch.set_facecolor("white")
    ax1.set_facecolor("white")
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.grid(axis="y", color=GRID, linestyle="--", alpha=0.7)
    ax1.set_axisbelow(True)

    b_fatigue = ax1.bar(x1, y1, color=c1, width=0.5, zorder=3)
    ax1.set_title("Diminishing Returns of Telemarketing: Conversion Rate Drops from 13.0% to 6.0% (Calls 7+)", fontsize=12, pad=12)
    ax1.set_xlabel("Call Sequence (Number of Times Lead Was Contacted)", fontsize=10)
    ax1.set_ylabel("Conversion Rate (%)", fontsize=10)
    ax1.set_ylim(0, 16.5)

    for b in b_fatigue:
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width() / 2, h + 0.4,
                 f"{h:.1f}%", ha="center", va="bottom",
                 fontweight="bold", fontsize=9.5, color=INK)

    # Threshold separator line at Call 3
    ax1.axvline(2.5, color=RED, linewidth=1.8, linestyle=":", label="3-Strike Policy Cut-Off")
    ax1.text(2.6, 14.5, "Sweet Spot: 88% Conversions Secured\nCalls 4+ yield diminishing returns",
             color=RED, fontweight="bold", fontsize=9)
    ax1.legend(loc="upper right", frameon=True, fontsize=9)
    fig1.tight_layout()
    out1 = FIG / "01_call_sequence_diminishing_returns.png"
    fig1.savefig(out1, dpi=160)
    plt.close(fig1)
    print(f"Generated {out1}")

    # =========================================================================
    # 3. STANDALONE FIGURE 2: 3-STRIKE EFFICIENCY COMPARISON (02_3strike_efficiency_comparison.png)
    # =========================================================================
    fig2, ax2 = plt.subplots(figsize=(10, 5.5), dpi=160)
    fig2.patch.set_facecolor("white")
    ax2.set_facecolor("white")
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.grid(axis="y", color=GRID, linestyle="--", alpha=0.7)
    ax2.set_axisbelow(True)

    metrics_comp = ["Total Dials (Volume)", "Deposit Conversions", "Labor Cost (€)"]
    pct_calls_1_3 = [81.5, 88.0, 81.5]
    pct_calls_4_plus = [18.5, 12.0, 18.5]
    x_idx = np.arange(len(metrics_comp))
    w_comp = 0.35

    b_c13 = ax2.bar(x_idx - w_comp/2, pct_calls_1_3, width=w_comp, color=GREEN, label="Calls 1–3 (Sweet Spot)", zorder=3)
    b_c4p = ax2.bar(x_idx + w_comp/2, pct_calls_4_plus, width=w_comp, color=RED, label="Calls 4+ (Wasteful Capacity)", zorder=3)

    ax2.set_title("Operational Efficiency Audit: Calls 1–3 vs Calls 4+ Capacity Allocation", fontsize=12, pad=12)
    ax2.set_xticks(x_idx)
    ax2.set_xticklabels(metrics_comp, fontsize=10, fontweight="bold")
    ax2.set_ylabel("Share of Total (%)", fontsize=10)
    ax2.set_ylim(0, 105)
    ax2.legend(loc="upper right", frameon=True, fontsize=9.5)

    for b in list(b_c13) + list(b_c4p):
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width() / 2, h + 1.5,
                 f"{h:.1f}%", ha="center", va="bottom",
                 fontweight="bold", fontsize=9.5, color=INK)

    fig2.tight_layout()
    out2 = FIG / "02_3strike_efficiency_comparison.png"
    fig2.savefig(out2, dpi=160)
    plt.close(fig2)
    print(f"Generated {out2}")

    # =========================================================================
    # 4. STANDALONE FIGURE 3: MACRO EURIBOR CONVERSION DROP (03_macro_euribor_conversion_drop.png)
    # =========================================================================
    fig3, ax3 = plt.subplots(figsize=(10, 5.5), dpi=160)
    fig3.patch.set_facecolor("white")
    ax3.set_facecolor("white")
    ax3.spines[["top", "right"]].set_visible(False)
    ax3.grid(axis="y", color=GRID, linestyle="--", alpha=0.7)
    ax3.set_axisbelow(True)

    b_m3 = ax3.bar(x3, y3, color=c3, width=0.48, zorder=3)
    ax3.set_title("Macroeconomic Elasticity: Term Deposit Conversions Collapse by -81% When Euribor > 4.0%", fontsize=12, pad=12)
    ax3.set_ylabel("Conversion Rate (%)", fontsize=10)
    ax3.set_ylim(0, 30)

    for b in b_m3:
        h = b.get_height()
        ax3.text(b.get_x() + b.get_width() / 2, h + 0.8,
                 f"{h:.1f}%", ha="center", va="bottom",
                 fontweight="bold", fontsize=10, color=INK)

    ax3.annotate("Monetary Tightening Effect:\n-81% Drop in Consumer Deposit Demand",
                 xy=(1.82, 3.2), xytext=(1.20, 19),
                 arrowprops=dict(facecolor=RED, shrink=0.08, width=2, headwidth=8),
                 fontweight="bold", color=RED, fontsize=9.5)

    fig3.tight_layout()
    out3 = FIG / "03_macro_euribor_conversion_drop.png"
    fig3.savefig(out3, dpi=160)
    plt.close(fig3)
    print(f"Generated {out3}")


if __name__ == "__main__":
    generate()
