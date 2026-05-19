import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

# ── Global style ──────────────────────────────────────────────────────────────
PLOT_STYLE = {
    "figure.facecolor": "#1e293b",
    "axes.facecolor":   "#0f172a",
    "axes.edgecolor":   "#334155",
    "axes.labelcolor":  "#94a3b8",
    "axes.titlecolor":  "#e2e8f0",
    "xtick.color":      "#64748b",
    "ytick.color":      "#64748b",
    "text.color":       "#e2e8f0",
    "grid.color":       "#1e293b",
    "grid.linewidth":   0.5,
    "axes.grid":        True,
}
plt.rcParams.update(PLOT_STYLE)

PRIMARY   = "#3b82f6"   # blue
SECONDARY = "#06b6d4"   # cyan
ACCENT    = "#8b5cf6"   # purple
SUCCESS   = "#22c55e"   # green
WARN      = "#f59e0b"   # amber
DANGER    = "#ef4444"   # red

PALETTE = [PRIMARY, SECONDARY, ACCENT, SUCCESS, WARN, DANGER,
            "#ec4899", "#14b8a6", "#f97316", "#a855f7"]


def _save(fig, path: Path) -> Path:
    fig.tight_layout()
    fig.savefig(path, dpi=120, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


# ── 1. Histogram ──────────────────────────────────────────────────────────────
def plot_histogram(df: pd.DataFrame, col: str, out_path: Path) -> Path:
    """Distribution histogram with KDE overlay."""
    fig, ax = plt.subplots(figsize=(7, 4))
    data = df[col].dropna()

    ax.hist(data, bins=25, color=PRIMARY, alpha=0.7, edgecolor="none")

    # KDE overlay
    try:
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(data)
        xs = np.linspace(data.min(), data.max(), 200)
        ax2 = ax.twinx()
        ax2.plot(xs, kde(xs), color=SECONDARY, linewidth=2)
        ax2.set_ylabel("Density", color=SECONDARY, fontsize=10)
        ax2.tick_params(colors=SECONDARY)
        ax2.set_facecolor("none")
    except Exception:
        pass

    ax.set_title(f"Distribution — {col}", fontsize=13, pad=10)
    ax.set_xlabel(col, fontsize=10)
    ax.set_ylabel("Frequency", fontsize=10)
    return _save(fig, out_path)


# ── 2. Bar Chart ──────────────────────────────────────────────────────────────
def plot_bar(df: pd.DataFrame, col: str, out_path: Path,
             top_n: int = 15) -> Path:
    """Horizontal bar chart for top-N categorical values."""
    counts = df[col].value_counts().head(top_n)

    fig, ax = plt.subplots(figsize=(8, max(4, len(counts) * 0.45)))
    bars = ax.barh(counts.index.astype(str)[::-1],
                   counts.values[::-1],
                   color=PALETTE[:len(counts)], edgecolor="none", height=0.7)

    # Value labels
    for bar in bars:
        w = bar.get_width()
        ax.text(w + max(counts) * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{int(w):,}", va="center", ha="left",
                color="#94a3b8", fontsize=9)

    ax.set_title(f"Top {top_n} — {col}", fontsize=13, pad=10)
    ax.set_xlabel("Count", fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return _save(fig, out_path)


# ── 3. Pie / Donut Chart ──────────────────────────────────────────────────────
def plot_pie(df: pd.DataFrame, col: str, out_path: Path,
             top_n: int = 8) -> Path:
    """Donut chart for categorical column."""
    counts = df[col].value_counts().head(top_n)
    if len(counts) > top_n:
        other = df[col].value_counts().iloc[top_n:].sum()
        counts["Other"] = other

    colors = PALETTE[:len(counts)]

    fig, ax = plt.subplots(figsize=(7, 6))
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=None,
        colors=colors,
        autopct="%1.1f%%",
        pctdistance=0.80,
        startangle=140,
        wedgeprops=dict(width=0.55, edgecolor="#0f172a", linewidth=2),
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(9)

    ax.legend(wedges, counts.index.astype(str),
              loc="lower center", ncol=3,
              framealpha=0, labelcolor="#94a3b8", fontsize=9,
              bbox_to_anchor=(0.5, -0.12))

    ax.set_title(f"Composition — {col}", fontsize=13, pad=15)
    return _save(fig, out_path)


# ── 4. Box Plot ───────────────────────────────────────────────────────────────
def plot_boxplot(df: pd.DataFrame, cols: List[str], out_path: Path) -> Path:
    """Side-by-side box plots for numeric columns."""
    data = [df[c].dropna().values for c in cols]
    labels = [c[:18] for c in cols]

    fig, ax = plt.subplots(figsize=(max(6, len(cols) * 1.8), 5))
    bp = ax.boxplot(data, labels=labels, patch_artist=True,
                    medianprops=dict(color=SECONDARY, linewidth=2),
                    whiskerprops=dict(color="#475569"),
                    capprops=dict(color="#475569"),
                    flierprops=dict(marker="o", markerfacecolor=DANGER,
                                   markersize=4, alpha=0.5))

    for patch, color in zip(bp["boxes"], PALETTE):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    ax.set_title("Box Plot — Numeric Columns", fontsize=13, pad=10)
    ax.set_ylabel("Value", fontsize=10)
    plt.xticks(rotation=25, ha="right", fontsize=9)
    return _save(fig, out_path)


# ── 5. Scatter Plot ───────────────────────────────────────────────────────────
def plot_scatter(df: pd.DataFrame, col_x: str, col_y: str,
                 out_path: Path) -> Path:
    """Scatter plot with trend line."""
    data = df[[col_x, col_y]].dropna()
    x, y = data[col_x].values, data[col_y].values

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(x, y, alpha=0.55, s=22, color=PRIMARY, edgecolors="none")

    # Trend line
    try:
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        xs = np.linspace(x.min(), x.max(), 200)
        ax.plot(xs, p(xs), color=SECONDARY, linewidth=1.5,
                linestyle="--", label="Trend")
        ax.legend(framealpha=0, labelcolor="#94a3b8", fontsize=9)
    except Exception:
        pass

    ax.set_title(f"Scatter — {col_x} vs {col_y}", fontsize=13, pad=10)
    ax.set_xlabel(col_x, fontsize=10)
    ax.set_ylabel(col_y, fontsize=10)
    return _save(fig, out_path)


# ── 6. Correlation Heatmap ────────────────────────────────────────────────────
def plot_correlation_heatmap(df: pd.DataFrame, out_path: Path) -> Path:
    """Correlation matrix heatmap for all numeric columns."""
    num_df = df.select_dtypes(include=[np.number])
    if num_df.shape[1] < 2:
        return None

    corr = num_df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)  # upper triangle
    mask = ~mask  # show lower triangle

    fig, ax = plt.subplots(figsize=(max(6, len(corr) * 0.9),
                                    max(5, len(corr) * 0.8)))

    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    sns.heatmap(corr, mask=~mask, cmap=cmap, vmin=-1, vmax=1, center=0,
                annot=True, fmt=".2f", annot_kws={"size": 8, "color": "white"},
                linewidths=0.3, linecolor="#0f172a",
                cbar_kws={"shrink": 0.7}, ax=ax)

    ax.set_title("Correlation Matrix", fontsize=13, pad=12)
    plt.xticks(rotation=30, ha="right", fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    return _save(fig, out_path)


# ── 7. Line Chart (time-series) ───────────────────────────────────────────────
def plot_line(df: pd.DataFrame, date_col: str, value_col: str,
              out_path: Path) -> Path:
    """Line chart for time-series data."""
    data = df[[date_col, value_col]].dropna().copy()
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    data = data.dropna(subset=[date_col]).sort_values(date_col)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(data[date_col], data[value_col],
            color=PRIMARY, linewidth=2, alpha=0.9)
    ax.fill_between(data[date_col], data[value_col],
                    alpha=0.15, color=PRIMARY)

    ax.set_title(f"{value_col} over time", fontsize=13, pad=10)
    ax.set_xlabel(date_col, fontsize=10)
    ax.set_ylabel(value_col, fontsize=10)
    plt.xticks(rotation=25, ha="right", fontsize=8)
    return _save(fig, out_path)


# ── 8. Summary stats card (text-based) ────────────────────────────────────────
def plot_summary_card(df: pd.DataFrame, out_path: Path) -> Path:
    """Text-based summary statistics card."""
    num_df = df.select_dtypes(include=[np.number])
    stats = num_df.describe().T[["mean", "std", "min", "max"]]

    fig, ax = plt.subplots(figsize=(9, max(3, len(stats) * 0.55 + 1)))
    ax.axis("off")

    headers = ["Column", "Mean", "Std Dev", "Min", "Max"]
    rows = []
    for col, row in stats.iterrows():
        rows.append([
            str(col)[:20],
            f"{row['mean']:,.2f}",
            f"{row['std']:,.2f}",
            f"{row['min']:,.2f}",
            f"{row['max']:,.2f}",
        ])

    table = ax.table(
        cellText=rows,
        colLabels=headers,
        cellLoc="right",
        loc="center",
        bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)

    # Header style
    for j in range(len(headers)):
        cell = table[0, j]
        cell.set_facecolor("#1e3a5f")
        cell.set_text_props(color="white", fontweight="bold")

    # Row alternating colors
    for i in range(1, len(rows) + 1):
        for j in range(len(headers)):
            cell = table[i, j]
            cell.set_facecolor("#0f172a" if i % 2 == 0 else "#1e293b")
            cell.set_text_props(color="#94a3b8")
            cell.set_edgecolor("#334155")

    ax.set_title("Summary Statistics", fontsize=13,
                 color="#e2e8f0", pad=14)
    return _save(fig, out_path)


# ── Master function ────────────────────────────────────────────────────────────
def generate_all_charts(df: pd.DataFrame, out_dir: Path) -> Dict[str, Any]:
    """
    Smart chart generation:
    - Histograms for all numeric columns
    - Bar charts for categorical columns
    - Pie chart for first categorical column
    - Scatter for first pair of numeric columns
    - Correlation heatmap if ≥2 numeric cols
    - Box plot if ≥2 numeric cols
    - Summary stats table
    - Line chart if date column found

    Returns dict mapping chart_name → file path
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    charts: Dict[str, Path] = {}

    numeric_cols   = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # Date columns
    date_cols = []
    for c in df.columns:
        if df[c].dtype == "datetime64[ns]" or (df[c].dtype == object and
                pd.to_datetime(df[c], errors="coerce").notna().mean() > 0.7):
            date_cols.append(c)

    # 1. Histograms (up to 6 numeric cols)
    for col in numeric_cols[:6]:
        safe = col.replace(" ", "_")[:30]
        p = plot_histogram(df, col, out_dir / f"hist_{safe}.png")
        if p:
            charts[f"hist_{safe}"] = p

    # 2. Bar charts (up to 3 categorical cols)
    for col in categorical_cols[:3]:
        if df[col].nunique() <= 50:
            safe = col.replace(" ", "_")[:30]
            p = plot_bar(df, col, out_dir / f"bar_{safe}.png")
            if p:
                charts[f"bar_{safe}"] = p

    # 3. Pie chart for first categorical col with few categories
    for col in categorical_cols[:2]:
        if 2 <= df[col].nunique() <= 15:
            safe = col.replace(" ", "_")[:30]
            p = plot_pie(df, col, out_dir / f"pie_{safe}.png")
            if p:
                charts[f"pie_{safe}"] = p
            break

    # 4. Correlation heatmap
    if len(numeric_cols) >= 2:
        p = plot_correlation_heatmap(df, out_dir / "correlation_heatmap.png")
        if p:
            charts["correlation_heatmap"] = p

    # 5. Box plot
    if len(numeric_cols) >= 2:
        cols_for_box = numeric_cols[:8]
        p = plot_boxplot(df, cols_for_box, out_dir / "boxplot.png")
        if p:
            charts["boxplot"] = p

    # 6. Scatter (first two numeric cols)
    if len(numeric_cols) >= 2:
        p = plot_scatter(df, numeric_cols[0], numeric_cols[1],
                         out_dir / "scatter.png")
        if p:
            charts["scatter"] = p

    # 7. Line chart (if date col found + numeric col)
    if date_cols and numeric_cols:
        p = plot_line(df, date_cols[0], numeric_cols[0],
                      out_dir / "line_chart.png")
        if p:
            charts["line_chart"] = p

    # 8. Summary stats table
    if numeric_cols:
        p = plot_summary_card(df, out_dir / "summary_stats.png")
        if p:
            charts["summary_stats"] = p

    return charts
