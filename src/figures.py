"""Figure functions. Each takes the data, saves a PNG to figures/ and returns
the numbers its reading note was built from, so notes never hold typed-in values."""
import textwrap
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FIG_DIR = Path(__file__).resolve().parents[1] / "figures"

# Reference palette (dataviz skill, light mode): slot 1 blue, slot 2 orange.
BLUE, ORANGE = "#2a78d6", "#eb6834"
SURFACE, INK, INK_2, GRID, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e0", "#a3a29c"
GROUP_COLORS = {"Student": BLUE, "Professional": ORANGE}
SOURCE = "Source: Kaggle, AI Usage and Impact on Students and Professionals (CC0). Synthetic data."

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK_2, "xtick.color": INK_2, "ytick.color": INK_2,
    "text.color": INK, "font.size": 10, "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
})


def spearman(x: pd.Series, y: pd.Series) -> float:
    """Spearman rho as Pearson on average ranks (avoids a scipy dependency)."""
    return x.rank().corr(y.rank())


def _finish(fig, note: str, name: str) -> Path:
    """Add the reading note + source under the plot and save."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)  # suptitle layouts warn but render fine
        fig.tight_layout()
    text = "\n".join(textwrap.wrap(note, 125) + [SOURCE])
    fig.text(0.01, -0.01, text, ha="left", va="top", fontsize=9, color=INK_2)
    FIG_DIR.mkdir(exist_ok=True)
    path = FIG_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def missing_before_after(raw: pd.DataFrame, clean: pd.DataFrame) -> dict:
    cols = list(raw.columns)
    before = raw[cols].isna().mean() * 100
    after = clean[cols].isna().mean() * 100
    order = after.sort_values().index
    y = np.arange(len(order))
    fig, ax = plt.subplots(figsize=(9, 7.5))
    h = 0.38
    ax.barh(y + h / 2, before[order], height=h, color=MUTED, label=f"Raw ({len(raw)} rows)")
    ax.barh(y - h / 2, after[order], height=h, color=BLUE, label=f"Cleaned ({len(clean)} rows)")
    ax.set_yticks(y, order)
    ax.set_xlabel("Missing values (% of rows)")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", frameon=False)
    ax.set_title("Missing values by column, before and after cleaning")
    top = after.idxmax()
    complete = int(clean[cols].notna().all(axis=1).sum())
    note = (f"Reading: after cleaning {top} has the most missing values ({after[top]:.1f}%), and only "
            f"{complete} of {len(clean)} rows are complete; no values were imputed (synthetic data).")
    _finish(fig, note, "01_missing_values")
    return {"top_col": top, "top_pct": round(after[top], 1), "complete_rows": complete, "n": len(clean)}


def tool_standardization(raw: pd.DataFrame, clean: pd.DataFrame) -> dict:
    u_before, u_after = raw["AI_Tool"].nunique(), clean["AI_Tool"].nunique()
    counts = clean["AI_Tool"].value_counts().sort_values()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), gridspec_kw={"width_ratios": [1, 2.4], "wspace": 0.5})
    ax1.bar(["Raw", "Cleaned"], [u_before, u_after], color=[MUTED, BLUE], width=0.55)
    for x, v in enumerate([u_before, u_after]):
        ax1.text(x, v + 0.3, str(v), ha="center", color=INK, fontweight="bold")
    ax1.set_ylabel("Distinct AI_Tool spellings (count)")
    ax1.grid(axis="x", visible=False)
    ax1.set_title("Distinct tool names", fontsize=11)
    ax2.barh(counts.index, counts.values, color=BLUE, height=0.6)
    for i, v in enumerate(counts.values):
        ax2.text(v + 1, i, str(v), va="center", color=INK_2, fontsize=9)
    ax2.set_xlabel("Users (count)")
    ax2.grid(axis="y", visible=False)
    ax2.set_title(f"Cleaned tool distribution (n = {int(counts.sum())})", fontsize=11)
    fig.suptitle("AI_Tool: effect of standardizing spellings", x=0.01, ha="left", fontweight="bold", fontsize=13)
    top = counts.index[-1]
    note = (f"Reading: merging spelling variants cut AI_Tool from {u_before} to {u_after} values, and {top} "
            f"is the most common tool ({counts[top]} of {int(counts.sum())} users with a tool; synthetic data).")
    _finish(fig, note, "02_ai_tool_standardization")
    return {"before": u_before, "after": u_after, "top": top, "top_n": int(counts[top]), "n": int(counts.sum())}


def usage_by_user_type(clean: pd.DataFrame) -> dict:
    d = clean[["User_Type", "AI_Usage_Hours_Per_Day"]].dropna()
    groups = ["Student", "Professional"]
    fig, ax = plt.subplots(figsize=(9, 5))
    bins = np.arange(0, d["AI_Usage_Hours_Per_Day"].max() + 1, 0.5)
    stats = {}
    for g in groups:
        s = d.loc[d["User_Type"] == g, "AI_Usage_Hours_Per_Day"]
        stats[g] = {"n": len(s), "median": s.median(), "q1": s.quantile(0.25), "q3": s.quantile(0.75)}
        ax.hist(s, bins=bins, histtype="step", linewidth=2, color=GROUP_COLORS[g],
                label=f"{g} (n = {len(s)}, median {s.median():.2f} h)")
        ax.axvline(s.median(), color=GROUP_COLORS[g], linestyle="--", linewidth=1.2)
    ax.set_xlabel("AI usage (hours per day)")
    ax.set_ylabel("Users (count per 0.5 h bin)")
    ax.legend(frameon=False)
    ax.set_title("Daily AI usage by user type")
    st, pr = stats["Student"], stats["Professional"]
    note = (f"Reading: in this dataset both groups are right-skewed with similar medians "
            f"(students {st['median']:.2f} h, professionals {pr['median']:.2f} h per day; dashed lines; synthetic data).")
    _finish(fig, note, "03_usage_by_user_type")
    return stats


def usage_vs_productivity(clean: pd.DataFrame) -> dict:
    d = clean[["User_Type", "AI_Usage_Hours_Per_Day", "Productivity_Score"]].dropna()
    rho = spearman(d["AI_Usage_Hours_Per_Day"], d["Productivity_Score"])
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for g in ["Student", "Professional"]:
        s = d[d["User_Type"] == g]
        ax.scatter(s["AI_Usage_Hours_Per_Day"], s["Productivity_Score"], s=28, color=GROUP_COLORS[g],
                   alpha=0.75, edgecolor=SURFACE, linewidth=1, label=f"{g} (n = {len(s)})")
    ax.set_xlabel("AI usage (hours per day)")
    ax.set_ylabel(f"Productivity_Score (observed range {d['Productivity_Score'].min():g}-{d['Productivity_Score'].max():g})")
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("AI usage and Productivity_Score")
    note = (f"Reading: in this dataset Spearman rho = {rho:.2f} (n = {len(d)}): rows with more daily usage tend to have "
            f"higher scores. This is a pattern in synthetic data, not evidence that usage causes productivity.")
    _finish(fig, note, "04_usage_vs_productivity")
    return {"rho": round(rho, 3), "n": len(d)}


def satisfaction_by_purpose(clean: pd.DataFrame) -> dict:
    d = clean[["AI_Purpose", "Satisfaction_Score"]].dropna()
    g = d.groupby("AI_Purpose")["Satisfaction_Score"].agg(["mean", "median", "count"]).sort_values("mean")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(g.index, g["mean"], color=BLUE, height=0.6)
    for i, (m, n) in enumerate(zip(g["mean"], g["count"])):
        ax.text(m + 0.05, i, f"{m:.2f}  (n = {n})", va="center", color=INK_2, fontsize=9)
    ax.set_xlim(0, 10)
    ax.set_xlabel(f"Mean Satisfaction_Score (observed range {d['Satisfaction_Score'].min():g}-{d['Satisfaction_Score'].max():g})")
    ax.grid(axis="y", visible=False)
    ax.set_title("Mean Satisfaction_Score by AI purpose")
    lo, hi = g.index[0], g.index[-1]
    medians = (f"every group median is {g['median'].iloc[0]:g}" if g["median"].nunique() == 1
               else f"group medians range {g['median'].min():g}-{g['median'].max():g}")
    note = (f"Reading: in this dataset group means only span {g['mean'].min():.2f} ({lo}) to {g['mean'].max():.2f} "
            f"({hi}), {medians}, and the smallest group has n = {g['count'].min()} (synthetic data).")
    _finish(fig, note, "05_satisfaction_by_purpose")
    return {"table": g.round(2), "n": len(d)}


def satisfaction_paid_vs_free(clean: pd.DataFrame) -> dict:
    d = clean[["Monthly_AI_Cost", "Satisfaction_Score"]].dropna().copy()
    d["Plan"] = np.where(d["Monthly_AI_Cost"] > 0, "Paid (cost > 0)", "Free (cost = 0)")
    scores = np.arange(d["Satisfaction_Score"].min(), d["Satisfaction_Score"].max() + 1)
    fig, ax = plt.subplots(figsize=(9, 5))
    w = 0.38
    out = {}
    for i, (plan, color) in enumerate([("Free (cost = 0)", MUTED), ("Paid (cost > 0)", BLUE)]):
        s = d.loc[d["Plan"] == plan, "Satisfaction_Score"]
        share = s.value_counts(normalize=True).reindex(scores, fill_value=0) * 100
        ax.bar(scores + (i - 0.5) * w, share, width=w, color=color,
               label=f"{plan}: n = {len(s)}, median {s.median():g}, mean {s.mean():.2f}")
        out[plan] = {"n": len(s), "median": s.median(), "mean": round(s.mean(), 2)}
    ax.set_xticks(scores)
    ax.set_ylim(0, ax.get_ylim()[1] * 1.25)
    ax.set_xlabel("Satisfaction_Score (integer score)")
    ax.set_ylabel("Share of group (%)")
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False)
    ax.set_title("Satisfaction_Score: paid vs free users")
    fr, pa = out["Free (cost = 0)"], out["Paid (cost > 0)"]
    note = (f"Reading: in this dataset medians are {fr['median']:g} (free) and {pa['median']:g} (paid), "
            f"means {fr['mean']:.2f} vs {pa['mean']:.2f}; the distributions largely overlap (synthetic data).")
    _finish(fig, note, "06_satisfaction_paid_vs_free")
    return out
