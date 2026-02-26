# =============================================================================
# COVID-19 Global Data Analysis
# Author   : Rensee Gajipara
# GitHub   : github.com/RENSEE-GAJIPARA
# Tools    : Python, Pandas, Matplotlib, Seaborn
# Dataset  : covid19_global_data.csv (included in project folder)
# Focus    : France, Italy, Russia, South Africa, Australia
# =============================================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings
warnings.filterwarnings("ignore")

# ── Output folder ──────────────────────────────────────────────────────────────
OUTPUT_DIR = "output_charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Plot style ─────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
COLORS = ["#2C7BB6", "#D7191C", "#1A9641", "#FDAE61", "#7B2D8B"]
plt.rcParams.update({"font.family": "DejaVu Sans", "figure.dpi": 150})

FOCUS = ["France", "Italy", "Russia", "South Africa", "Australia"]

# =============================================================================
# 1. LOAD DATA
# =============================================================================
print("=" * 60)
print("  COVID-19 Global Data Analysis -- Rensee Gajipara")
print("=" * 60)
print("\n[1/7] Loading dataset...")

CSV_FILE = "covid19_global_data.csv"
if not os.path.exists(CSV_FILE):
    print(f"ERROR: '{CSV_FILE}' not found!")
    print("Make sure covid19_global_data.csv is in the same folder.")
    exit(1)

df = pd.read_csv(CSV_FILE, parse_dates=["Date"])
print(f"      Loaded {len(df):,} rows | {df['Country'].nunique()} countries in dataset")

# =============================================================================
# 2. CLEAN & PREPARE
# =============================================================================
print("\n[2/7] Preparing and cleaning data...")

df_focus = df[df["Country"].isin(FOCUS)].copy().sort_values(["Country", "Date"])

# 4-week rolling average
for col in ["Weekly_New_Cases", "Weekly_New_Deaths"]:
    df_focus[f"{col}_avg"] = (
        df_focus.groupby("Country")[col]
        .transform(lambda x: x.rolling(4, min_periods=1).mean())
    )

# Monthly aggregation for peak wave detection
df_focus["Month"] = df_focus["Date"].dt.to_period("M")

print(f"      Date range  : {df['Date'].min().date()} → {df['Date'].max().date()}")
print(f"      Focus       : {', '.join(FOCUS)}")
print(f"      Missing vals: {df_focus.isnull().sum().sum()}")

latest = df_focus.groupby("Country").last().reset_index()

# =============================================================================
# 3. CHART 1 — Weekly Cases Over Time (Rolling Average)
# =============================================================================
print("\n[3/7] Chart 1: Weekly cases & deaths over time...")

fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
fig.suptitle(
    "COVID-19: Weekly Cases & Deaths Over Time\n(4-Week Rolling Average | France, Italy, Russia, South Africa, Australia)",
    fontsize=14, fontweight="bold", y=0.99
)

for i, (col, label) in enumerate([
    ("Weekly_New_Cases_avg",  "Weekly New Cases"),
    ("Weekly_New_Deaths_avg", "Weekly New Deaths"),
]):
    ax = axes[i]
    for j, country in enumerate(FOCUS):
        data = df_focus[df_focus["Country"] == country]
        ax.plot(data["Date"], data[col], label=country,
                color=COLORS[j], linewidth=1.8)
    ax.set_ylabel(label, fontsize=11)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.legend(loc="upper left", fontsize=9, framealpha=0.7)
    ax.set_facecolor("#F9FBFC")

axes[1].set_xlabel("Date", fontsize=11)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/1_cases_deaths_over_time.png", bbox_inches="tight")
plt.close()
print("      Saved: 1_cases_deaths_over_time.png")

# =============================================================================
# 4. CHART 2 — Population-Adjusted Country Comparison
# =============================================================================
print("\n[4/7] Chart 2: Population-adjusted country comparison...")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Population-Adjusted Comparison: Cases & Deaths per Million",
             fontsize=14, fontweight="bold")

for ax, (col, title, color) in zip(axes, [
    ("Cases_Per_Million",  "Total Cases per Million",  COLORS[0]),
    ("Deaths_Per_Million", "Total Deaths per Million", COLORS[1]),
]):
    plot_data = latest[["Country", col]].dropna().sort_values(col, ascending=True)
    bars = ax.barh(plot_data["Country"], plot_data[col],
                   color=color, edgecolor="white", height=0.55)
    ax.bar_label(bars, fmt="{:,.0f}", padding=4, fontsize=9)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel("Per Million Population", fontsize=10)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.set_facecolor("#F9FBFC")

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/2_country_comparison.png", bbox_inches="tight")
plt.close()
print("      Saved: 2_country_comparison.png")

# =============================================================================
# 5. CHART 3 — Vaccination Progress
# =============================================================================
print("\n[5/7] Chart 3: Vaccination progress...")

df_vax = df_focus[["Date", "Country", "Vaccinated_Pct"]].dropna()

fig, ax = plt.subplots(figsize=(14, 6))
for j, country in enumerate(FOCUS):
    data = df_vax[df_vax["Country"] == country]
    ax.plot(data["Date"], data["Vaccinated_Pct"],
            label=country, color=COLORS[j], linewidth=2)

ax.axhline(70, color="gray", linestyle="--", linewidth=1.2,
           alpha=0.7, label="70% Herd Immunity Target")
ax.fill_between(df_vax["Date"].unique(), 70, 100, alpha=0.05, color="green")
ax.set_title("Vaccination Rollout Progress: % Population Vaccinated (At Least 1 Dose)",
             fontsize=13, fontweight="bold")
ax.set_ylabel("% Population Vaccinated", fontsize=11)
ax.set_xlabel("Date", fontsize=11)
ax.set_ylim(0, 105)
ax.legend(fontsize=10, framealpha=0.7)
ax.set_facecolor("#F9FBFC")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/3_vaccination_progress.png", bbox_inches="tight")
plt.close()
print("      Saved: 3_vaccination_progress.png")

# =============================================================================
# 6. CHART 4 — Case Fatality Rate Comparison
# =============================================================================
print("\n[6/7] Chart 4: Case fatality rate...")

cfr_data = latest[["Country", "Case_Fatality_Rate_Pct"]].dropna().sort_values(
    "Case_Fatality_Rate_Pct", ascending=True)

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(cfr_data["Country"], cfr_data["Case_Fatality_Rate_Pct"],
               color=COLORS[2], edgecolor="white", height=0.5)
ax.bar_label(bars, fmt="{:.2f}%", padding=4, fontsize=10)
ax.set_title("Case Fatality Rate (CFR) by Country\n(Total Deaths / Total Cases × 100)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Case Fatality Rate (%)", fontsize=11)
ax.set_facecolor("#F9FBFC")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/4_case_fatality_rate.png", bbox_inches="tight")
plt.close()
print("      Saved: 4_case_fatality_rate.png")

# =============================================================================
# 7. CHART 5 — Recovery Rate Trend (NEW)
# =============================================================================
print("\n[7/7] Chart 5: Recovery rate trend (new analysis)...")

df_rec = df_focus[["Date", "Country", "Recovery_Rate_Pct"]].dropna()

fig, ax = plt.subplots(figsize=(14, 6))
for j, country in enumerate(FOCUS):
    data = df_rec[df_rec["Country"] == country]
    ax.plot(data["Date"], data["Recovery_Rate_Pct"],
            label=country, color=COLORS[j], linewidth=2)

ax.axhline(95, color="green", linestyle="--", linewidth=1.2,
           alpha=0.6, label="95% Recovery Benchmark")
ax.set_title("Recovery Rate Trend Over Time by Country",
             fontsize=13, fontweight="bold")
ax.set_ylabel("Recovery Rate (%)", fontsize=11)
ax.set_xlabel("Date", fontsize=11)
ax.set_ylim(80, 102)
ax.legend(fontsize=10, framealpha=0.7)
ax.set_facecolor("#F9FBFC")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/5_recovery_rate_trend.png", bbox_inches="tight")
plt.close()
print("      Saved: 5_recovery_rate_trend.png")

# =============================================================================
# 8. SUMMARY REPORT
# =============================================================================
print("\n" + "=" * 60)
print("  SUMMARY REPORT")
print("=" * 60)

for country in FOCUS:
    row = latest[latest["Country"] == country]
    if row.empty:
        continue
    row = row.iloc[0]
    print(f"\n  {country}")
    print(f"    Total Cases      : {row['Cumulative_Cases']:>15,.0f}")
    print(f"    Total Deaths     : {row['Cumulative_Deaths']:>15,.0f}")
    print(f"    Cases/Million    : {row['Cases_Per_Million']:>15,.0f}")
    print(f"    Deaths/Million   : {row['Deaths_Per_Million']:>15,.2f}")
    print(f"    CFR              : {row['Case_Fatality_Rate_Pct']:>13.2f}%")
    print(f"    Vaccinated       : {row['Vaccinated_Pct']:>13.1f}%")
    print(f"    Recovery Rate    : {row['Recovery_Rate_Pct']:>13.1f}%")

print("\n" + "=" * 60)
print(f"  5 charts saved to -> ./{OUTPUT_DIR}/")
print("=" * 60)
print("\nAnalysis complete! Open output_charts/ to view all charts.\n")
