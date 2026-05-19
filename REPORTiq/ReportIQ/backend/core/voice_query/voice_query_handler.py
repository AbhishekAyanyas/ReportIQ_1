"""
Improved Voice Query Handler — REPORTiq
=======================================
Upgrades over old version:
  • rapidfuzz fuzzy column matching  (handles typos + multi-word columns)
  • Intent detection before regex    (no more missed patterns)
  • Synonym map                      (sales→revenue, profit→margin, etc.)
  • New query types:
        trend, best/worst category, anomaly detection,
        group-by, percentage, std-dev, distribution
  • Works on the CLEANED dataframe loaded from file
  • Falls back gracefully with a helpful hint message
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# ── Optional: rapidfuzz for fuzzy column matching ──────────────────────────
try:
    from rapidfuzz import process as rf_process, fuzz as rf_fuzz
    _RAPIDFUZZ = True
except ImportError:
    _RAPIDFUZZ = False

# ── Synonym map ────────────────────────────────────────────────────────────
# Maps common business words → possible column name fragments
SYNONYMS: dict[str, list[str]] = {
    "sales":    ["sales", "revenue", "amount", "income", "turnover"],
    "profit":   ["profit", "margin", "earnings", "gain", "net"],
    "cost":     ["cost", "expense", "expenditure", "spend"],
    "quantity": ["qty", "quantity", "units", "count", "volume"],
    "price":    ["price", "rate", "value", "cost"],
    "date":     ["date", "month", "year", "day", "time", "period"],
    "customer": ["customer", "client", "buyer", "user"],
    "product":  ["product", "item", "sku", "category", "name"],
    "region":   ["region", "city", "state", "country", "location", "area"],
}

# ── Intent keywords ────────────────────────────────────────────────────────
INTENTS: list[tuple[str, list[str]]] = [
    ("trend",       ["trend", "over time", "monthly", "yearly", "growth", "decline",
                     "progress", "series"]),
    ("anomaly",     ["anomaly", "anomalies", "unusual", "spike", "outlier", "outliers",
                     "strange", "weird"]),
    ("best",        ["best", "highest", "top performing", "top category", "most",
                     "leading", "largest"]),
    ("worst",       ["worst", "lowest", "least", "bottom", "smallest", "poor"]),
    ("sum",         ["total", "sum", "add up", "aggregate"]),
    ("average",     ["average", "mean", "avg"]),
    ("max",         ["maximum", "max", "highest value", "peak"]),
    ("min",         ["minimum", "min", "lowest value"]),
    ("count",       ["how many", "count", "number of", "records", "rows", "entries"]),
    ("stddev",      ["std", "standard deviation", "deviation", "variance", "spread"]),
    ("percent",     ["percent", "percentage", "%", "share", "proportion", "ratio"]),
    ("groupby",     ["group by", "grouped", "by category", "per category",
                     "break down", "breakdown"]),
    ("correlation", ["correlation", "correl", "relationship between", "relation between",
                     "linked to", "related to"]),
    ("missing",     ["missing", "null", "empty", "nan", "incomplete"]),
    ("unique",      ["unique", "distinct", "different values"]),
    ("summary",     ["summary", "describe", "overview", "info", "about the data",
                     "dataset info"]),
    ("columns",     ["columns", "fields", "attributes", "headers", "what columns"]),
    ("top_n",       ["top", "first", "show me top", "show top"]),
    ("bottom_n",    ["bottom", "last", "show me bottom", "show bottom",
                     "worst performing"]),
    ("distribution",["distribution", "histogram", "spread of", "values of"]),
]


class VoiceQueryHandler:
    """
    Handles text / voice queries against a pandas DataFrame.

    Usage
    -----
    handler = VoiceQueryHandler("abc123", Path("static/uploads/abc123.csv"))
    result  = handler.process_query("What is the total sales?")
    """

    def __init__(self, report_id: str, data_path: Path):
        self.report_id = report_id
        self.df = self._load(data_path)
        self._refresh_meta()

    # ──────────────────────────────────────────────────────────────────
    # Public
    # ──────────────────────────────────────────────────────────────────

    def process_query(self, query: str) -> dict[str, Any]:
        """Main entry point. Returns a response dict with 'answer' key."""
        q = query.lower().strip()
        intent = self._detect_intent(q)
        return self._dispatch(intent, q)

    def get_suggestions(self) -> list[str]:
        """Return context-aware example queries for the UI."""
        suggestions = [
            "How many records are there?",
            "Give me the dataset summary",
            "Are there any missing values?",
            "What columns are in the dataset?",
        ]
        for col in self.numeric_cols[:3]:
            suggestions += [
                f"What is the total {col}?",
                f"What is the average {col}?",
                f"Show me the trend of {col}",
                f"Top 5 by {col}",
                f"Any anomalies in {col}?",
            ]
        for col in self.cat_cols[:2]:
            suggestions += [
                f"Best category in {col}?",
                f"How many unique values in {col}?",
            ]
        if len(self.numeric_cols) >= 2:
            c1, c2 = self.numeric_cols[0], self.numeric_cols[1]
            suggestions.append(f"Correlation between {c1} and {c2}?")
        return suggestions[:20]

    # ──────────────────────────────────────────────────────────────────
    # Loading + meta
    # ──────────────────────────────────────────────────────────────────

    def _load(self, path: Path) -> pd.DataFrame:
        if path.suffix.lower() == ".csv":
            return pd.read_csv(path)
        elif path.suffix.lower() in (".xlsx", ".xls"):
            return pd.read_excel(path)
        raise ValueError(f"Unsupported format: {path.suffix}")

    def _refresh_meta(self):
        """Recompute column lists (call again if df changes)."""
        self.numeric_cols  = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.cat_cols      = self.df.select_dtypes(include=["object", "category"]).columns.tolist()
        self.date_cols     = [c for c in self.df.columns
                              if pd.api.types.is_datetime64_any_dtype(self.df[c])
                              or (self.df[c].dtype == object
                                  and pd.to_datetime(self.df[c], errors="coerce").notna().mean() > 0.6)]
        # lowercase → real column name map for fast lookup
        self._col_lower: dict[str, str] = {c.lower(): c for c in self.df.columns}

    # ──────────────────────────────────────────────────────────────────
    # Intent detection
    # ──────────────────────────────────────────────────────────────────

    def _detect_intent(self, q: str) -> str:
        """Return the best matching intent label."""
        for intent_name, keywords in INTENTS:
            for kw in keywords:
                if kw in q:
                    return intent_name
        return "unknown"

    # ──────────────────────────────────────────────────────────────────
    # Column matching
    # ──────────────────────────────────────────────────────────────────

    def _find_column(self, token: str, numeric_only: bool = False) -> str | None:
        """
        Find the best-matching column for a query token.
        Priority:
          1. Exact match (case-insensitive)
          2. Synonym expansion
          3. Substring match
          4. Rapidfuzz fuzzy match (if installed)
        """
        token = token.strip().lower()
        pool = self.numeric_cols if numeric_only else list(self.df.columns)

        # 1. Exact
        if token in self._col_lower:
            col = self._col_lower[token]
            return col if (not numeric_only or col in self.numeric_cols) else None

        # 2. Synonym expansion
        for syn_key, syn_list in SYNONYMS.items():
            if token in syn_list or syn_key == token:
                for syn in syn_list:
                    for col in pool:
                        if syn in col.lower():
                            return col

        # 3. Substring
        for col in pool:
            if token in col.lower() or col.lower() in token:
                return col

        # 4. Fuzzy (rapidfuzz)
        if _RAPIDFUZZ and pool:
            result = rf_process.extractOne(
                token,
                [c.lower() for c in pool],
                scorer=rf_fuzz.token_sort_ratio,
                score_cutoff=60,
            )
            if result:
                matched_lower, score, _ = result
                return self._col_lower.get(matched_lower)

        return None

    def _extract_columns_from_query(self, q: str, numeric_only: bool = False) -> list[str]:
        """Pull all column references mentioned anywhere in the query."""
        found: list[str] = []
        pool = self.numeric_cols if numeric_only else list(self.df.columns)

        # Check each column name (and its synonyms) against the query words
        for col in pool:
            words = re.split(r"[\s_\-]+", col.lower())
            if any(w in q for w in words if len(w) > 2):
                if col not in found:
                    found.append(col)

        # Also try synonym keys mentioned in the query
        for syn_key, syn_list in SYNONYMS.items():
            if syn_key in q or any(s in q for s in syn_list):
                col = self._find_column(syn_key, numeric_only)
                if col and col not in found:
                    found.append(col)

        return found

    # ──────────────────────────────────────────────────────────────────
    # Dispatcher
    # ──────────────────────────────────────────────────────────────────

    def _dispatch(self, intent: str, q: str) -> dict[str, Any]:
        handlers = {
            "sum":         self._h_sum,
            "average":     self._h_average,
            "max":         self._h_max,
            "min":         self._h_min,
            "stddev":      self._h_stddev,
            "percent":     self._h_percent,
            "count":       self._h_count,
            "columns":     self._h_columns,
            "top_n":       self._h_top_n,
            "bottom_n":    self._h_bottom_n,
            "trend":       self._h_trend,
            "best":        self._h_best_category,
            "worst":       self._h_worst_category,
            "anomaly":     self._h_anomaly,
            "groupby":     self._h_groupby,
            "correlation": self._h_correlation,
            "missing":     self._h_missing,
            "unique":      self._h_unique,
            "summary":     self._h_summary,
            "distribution":self._h_distribution,
            "unknown":     self._h_unknown,
        }
        handler = handlers.get(intent, self._h_unknown)
        try:
            return handler(q)
        except Exception as e:
            return self._err(f"Error processing query: {e}")

    # ──────────────────────────────────────────────────────────────────
    # Individual handlers
    # ──────────────────────────────────────────────────────────────────

    def _h_sum(self, q: str) -> dict:
        col = self._pick_numeric(q)
        if not col:
            return self._err("Kaunsa column ka total chahiye? (e.g. 'total sales')")
        total = self.df[col].sum()
        return self._ok("sum", f"Total {col} = {total:,.2f}", {"column": col, "result": float(total)})

    def _h_average(self, q: str) -> dict:
        col = self._pick_numeric(q)
        if not col:
            return self._err("Average kiske liye chahiye? (e.g. 'average price')")
        avg = self.df[col].mean()
        return self._ok("average", f"Average {col} = {avg:,.2f}", {"column": col, "result": float(avg)})

    def _h_max(self, q: str) -> dict:
        col = self._pick_numeric(q)
        if not col:
            return self._err("Maximum kiska dhundna hai?")
        val = self.df[col].max()
        return self._ok("max", f"Maximum {col} = {val:,.2f}", {"column": col, "result": float(val)})

    def _h_min(self, q: str) -> dict:
        col = self._pick_numeric(q)
        if not col:
            return self._err("Minimum kiska dhundna hai?")
        val = self.df[col].min()
        return self._ok("min", f"Minimum {col} = {val:,.2f}", {"column": col, "result": float(val)})

    def _h_stddev(self, q: str) -> dict:
        col = self._pick_numeric(q)
        if not col:
            return self._err("Standard deviation kiske liye chahiye?")
        std = self.df[col].std()
        return self._ok("stddev", f"Standard deviation of {col} = {std:,.2f}",
                        {"column": col, "result": float(std)})

    def _h_percent(self, q: str) -> dict:
        """What % share does each category have?"""
        cat_col = None
        for col in self.cat_cols:
            if col.lower() in q or any(w in q for w in col.lower().split("_")):
                cat_col = col
                break
        if not cat_col and self.cat_cols:
            cat_col = self.cat_cols[0]
        if not cat_col:
            return self._err("Koi categorical column nahi mila percentage ke liye.")
        pct = (self.df[cat_col].value_counts(normalize=True) * 100).round(2)
        top = pct.head(8).to_dict()
        lines = [f"  {k}: {v:.1f}%" for k, v in top.items()]
        return self._ok("percent",
                        f"Percentage distribution of '{cat_col}':\n" + "\n".join(lines),
                        {"column": cat_col, "distribution": top})

    def _h_count(self, q: str) -> dict:
        n = len(self.df)
        return self._ok("count", f"Dataset mein kul {n:,} records hain.", {"result": n})

    def _h_columns(self, q: str) -> dict:
        cols = self.df.columns.tolist()
        return self._ok("columns",
                        f"Dataset mein {len(cols)} columns hain: {', '.join(cols)}",
                        {"columns": cols})

    def _h_top_n(self, q: str) -> dict:
        n = self._extract_n(q, default=5)
        col = self._pick_numeric(q)
        if not col:
            return self._err(f"Top {n} kiske by chahiye? (e.g. 'top 5 by sales')")
        rows = self.df.nlargest(n, col)[self._display_cols(col)].to_dict("records")
        return self._ok("top_n",
                        f"Top {n} records by '{col}':",
                        {"column": col, "n": n, "records": rows})

    def _h_bottom_n(self, q: str) -> dict:
        n = self._extract_n(q, default=5)
        col = self._pick_numeric(q)
        if not col:
            return self._err(f"Bottom {n} kiske by chahiye? (e.g. 'bottom 5 by profit')")
        rows = self.df.nsmallest(n, col)[self._display_cols(col)].to_dict("records")
        return self._ok("bottom_n",
                        f"Bottom {n} records by '{col}':",
                        {"column": col, "n": n, "records": rows})

    def _h_trend(self, q: str) -> dict:
        """Show time-based trend for a numeric column."""
        num_col = self._pick_numeric(q)
        date_col = self._pick_date(q)

        if not date_col and self.date_cols:
            date_col = self.date_cols[0]
        if not num_col and self.numeric_cols:
            num_col = self.numeric_cols[0]
        if not date_col:
            return self._err("Trend ke liye koi date/time column nahi mila.")
        if not num_col:
            return self._err("Trend kiska dikhana hai? (e.g. 'trend of sales')")

        tmp = self.df[[date_col, num_col]].copy()
        tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
        tmp = tmp.dropna()
        monthly = tmp.groupby(tmp[date_col].dt.to_period("M"))[num_col].sum()
        if monthly.empty:
            return self._err("Date column parse nahi hua, trend nahi dikhaya ja sakta.")

        # Simple trend direction
        if len(monthly) >= 2:
            first_half = monthly.iloc[: len(monthly) // 2].mean()
            second_half = monthly.iloc[len(monthly) // 2 :].mean()
            direction = "⬆ badhta hua (upward)" if second_half > first_half else "⬇ girta hua (downward)"
        else:
            direction = "insufficient data"

        top_month = str(monthly.idxmax())
        low_month = str(monthly.idxmin())
        summary_rows = monthly.tail(6).to_dict()
        summary_str = {str(k): float(v) for k, v in summary_rows.items()}

        answer = (
            f"'{num_col}' ka trend ({date_col} ke basis pe):\n"
            f"  Direction  : {direction}\n"
            f"  Best month : {top_month} ({monthly.max():,.2f})\n"
            f"  Worst month: {low_month} ({monthly.min():,.2f})\n"
            f"  Recent data: {summary_str}"
        )
        return self._ok("trend", answer,
                        {"num_col": num_col, "date_col": date_col,
                         "direction": direction, "best_month": top_month,
                         "worst_month": low_month, "monthly_summary": summary_str})

    def _h_best_category(self, q: str) -> dict:
        """Which category has the highest total for a numeric column?"""
        cat_col = self._pick_categorical(q)
        num_col = self._pick_numeric(q)
        if not cat_col and self.cat_cols:
            cat_col = self.cat_cols[0]
        if not num_col and self.numeric_cols:
            num_col = self.numeric_cols[0]
        if not cat_col:
            return self._err("Koi categorical column nahi mila.")
        if not num_col:
            return self._err("Numeric column specify karo. (e.g. 'best category by sales')")

        grp = self.df.groupby(cat_col)[num_col].sum().sort_values(ascending=False)
        best = grp.index[0]
        top5 = grp.head(5).to_dict()
        answer = (
            f"'{cat_col}' ka best category '{num_col}' ke basis pe:\n"
            f"  🏆 {best} ({grp.iloc[0]:,.2f})\n"
            f"  Top 5: { {str(k): round(float(v),2) for k,v in top5.items()} }"
        )
        return self._ok("best_category", answer,
                        {"cat_col": cat_col, "num_col": num_col,
                         "best": str(best), "top5": {str(k): float(v) for k, v in top5.items()}})

    def _h_worst_category(self, q: str) -> dict:
        """Which category has the lowest total?"""
        cat_col = self._pick_categorical(q)
        num_col = self._pick_numeric(q)
        if not cat_col and self.cat_cols:
            cat_col = self.cat_cols[0]
        if not num_col and self.numeric_cols:
            num_col = self.numeric_cols[0]
        if not cat_col or not num_col:
            return self._err("Category aur numeric column dono chahiye.")

        grp = self.df.groupby(cat_col)[num_col].sum().sort_values()
        worst = grp.index[0]
        bottom5 = grp.head(5).to_dict()
        answer = (
            f"'{cat_col}' ka worst category '{num_col}' ke basis pe:\n"
            f"  ⚠ {worst} ({grp.iloc[0]:,.2f})"
        )
        return self._ok("worst_category", answer,
                        {"cat_col": cat_col, "num_col": num_col,
                         "worst": str(worst),
                         "bottom5": {str(k): float(v) for k, v in bottom5.items()}})

    def _h_anomaly(self, q: str) -> dict:
        """Detect outliers using IQR method on a numeric column."""
        col = self._pick_numeric(q)
        if not col and self.numeric_cols:
            col = self.numeric_cols[0]
        if not col:
            return self._err("Anomaly detection ke liye numeric column chahiye.")

        s = self.df[col].dropna()
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers = self.df[(self.df[col] < lower) | (self.df[col] > upper)]

        if outliers.empty:
            answer = f"'{col}' mein koi anomaly / outlier nahi mila. Data clean hai! ✅"
        else:
            vals = outliers[col].tolist()[:5]
            answer = (
                f"'{col}' mein {len(outliers)} outliers mile:\n"
                f"  IQR range: [{lower:,.2f} — {upper:,.2f}]\n"
                f"  Sample outlier values: {[round(v,2) for v in vals]}"
            )
        return self._ok("anomaly", answer,
                        {"column": col, "outlier_count": len(outliers),
                         "lower_bound": float(lower), "upper_bound": float(upper)})

    def _h_groupby(self, q: str) -> dict:
        """Group numeric column by categorical column."""
        cat_col = self._pick_categorical(q)
        num_col = self._pick_numeric(q)
        if not cat_col and self.cat_cols:
            cat_col = self.cat_cols[0]
        if not num_col and self.numeric_cols:
            num_col = self.numeric_cols[0]
        if not cat_col or not num_col:
            return self._err("Group by ke liye ek categorical aur ek numeric column chahiye.")

        grp = self.df.groupby(cat_col)[num_col].agg(["sum", "mean", "count"]).round(2)
        grp.columns = ["total", "average", "count"]
        grp = grp.sort_values("total", ascending=False).head(10)
        result = grp.to_dict("index")
        result = {str(k): v for k, v in result.items()}
        answer = f"'{num_col}' grouped by '{cat_col}' (top 10 by total):\n"
        for cat, stats in list(result.items())[:5]:
            answer += f"  {cat}: total={stats['total']:,.0f}, avg={stats['average']:,.2f}\n"
        return self._ok("groupby", answer.strip(),
                        {"cat_col": cat_col, "num_col": num_col, "groups": result})

    def _h_correlation(self, q: str) -> dict:
        """Correlation between two numeric columns."""
        cols = self._extract_columns_from_query(q, numeric_only=True)
        if len(cols) < 2:
            if len(self.numeric_cols) >= 2:
                cols = self.numeric_cols[:2]
            else:
                return self._err("Correlation ke liye 2 numeric columns chahiye.")

        col1, col2 = cols[0], cols[1]
        corr = float(self.df[col1].corr(self.df[col2]))
        strength = "strong" if abs(corr) > 0.7 else "moderate" if abs(corr) > 0.4 else "weak"
        direction = "positive (+ve)" if corr > 0 else "negative (-ve)"
        answer = (
            f"Correlation between '{col1}' and '{col2}' = {corr:.3f}\n"
            f"  → {strength} {direction} relationship"
        )
        return self._ok("correlation", answer,
                        {"col1": col1, "col2": col2, "correlation": corr,
                         "strength": strength, "direction": direction})

    def _h_missing(self, q: str) -> dict:
        missing = self.df.isnull().sum()
        missing = missing[missing > 0].to_dict()
        if not missing:
            return self._ok("missing", "Dataset mein koi missing values nahi hain. ✅", {})
        total = sum(missing.values())
        answer = (
            f"Total {total} missing values, {len(missing)} columns mein:\n"
            + "\n".join(f"  {c}: {v}" for c, v in missing.items())
        )
        return self._ok("missing", answer, {"missing_by_column": {str(k): int(v) for k, v in missing.items()}})

    def _h_unique(self, q: str) -> dict:
        col = self._find_column(self._last_word(q))
        if not col:
            # fallback: first categorical
            col = self.cat_cols[0] if self.cat_cols else None
        if not col:
            return self._err("Unique values kis column ke chahiye?")
        uc = int(self.df[col].nunique())
        samples = [str(v) for v in self.df[col].dropna().unique()[:8]]
        return self._ok("unique",
                        f"'{col}' mein {uc} unique values hain.\n  Sample: {', '.join(samples)}",
                        {"column": col, "unique_count": uc, "sample": samples})

    def _h_summary(self, q: str) -> dict:
        info = {
            "total_rows": len(self.df),
            "total_columns": len(self.df.columns),
            "numeric_columns": len(self.numeric_cols),
            "categorical_columns": len(self.cat_cols),
            "date_columns": len(self.date_cols),
            "missing_values": int(self.df.isnull().sum().sum()),
            "duplicate_rows": int(self.df.duplicated().sum()),
            "memory_mb": round(self.df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        }
        answer = (
            f"📊 Dataset Summary:\n"
            f"  Rows       : {info['total_rows']:,}\n"
            f"  Columns    : {info['total_columns']} "
            f"({info['numeric_columns']} numeric, {info['categorical_columns']} categorical, "
            f"{info['date_columns']} date)\n"
            f"  Missing    : {info['missing_values']}\n"
            f"  Duplicates : {info['duplicate_rows']}\n"
            f"  Memory     : {info['memory_mb']} MB"
        )
        return self._ok("summary", answer, info)

    def _h_distribution(self, q: str) -> dict:
        col = self._pick_numeric(q)
        if not col:
            return self._err("Distribution kiske liye dikhana hai?")
        s = self.df[col].dropna()
        stats = {
            "count": int(s.count()),
            "mean":  round(float(s.mean()), 2),
            "std":   round(float(s.std()), 2),
            "min":   round(float(s.min()), 2),
            "25%":   round(float(s.quantile(.25)), 2),
            "50%":   round(float(s.median()), 2),
            "75%":   round(float(s.quantile(.75)), 2),
            "max":   round(float(s.max()), 2),
        }
        answer = (
            f"'{col}' ki distribution:\n"
            + "\n".join(f"  {k}: {v}" for k, v in stats.items())
        )
        return self._ok("distribution", answer, {"column": col, "stats": stats})

    def _h_unknown(self, q: str) -> dict:
        return {
            "query_type": "unknown",
            "answer": (
                "Samajh nahi aaya 😕 — ye queries try karo:\n"
                "  • 'total sales', 'average profit'\n"
                "  • 'top 5 by revenue'\n"
                "  • 'trend of sales'\n"
                "  • 'best category by profit'\n"
                "  • 'anomalies in revenue'\n"
                "  • 'correlation between sales and profit'\n"
                "  • 'dataset summary'"
            ),
            "data": {},
        }

    # ──────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────

    def _pick_numeric(self, q: str) -> str | None:
        cols = self._extract_columns_from_query(q, numeric_only=True)
        return cols[0] if cols else None

    def _pick_categorical(self, q: str) -> str | None:
        for col in self.cat_cols:
            words = re.split(r"[\s_\-]+", col.lower())
            if any(w in q for w in words if len(w) > 2):
                return col
        return None

    def _pick_date(self, q: str) -> str | None:
        for col in self.date_cols:
            if any(w in q for w in re.split(r"[\s_\-]+", col.lower()) if len(w) > 2):
                return col
        return None

    def _extract_n(self, q: str, default: int = 5) -> int:
        m = re.search(r"\b(\d+)\b", q)
        return int(m.group(1)) if m else default

    def _last_word(self, q: str) -> str:
        words = q.strip().split()
        return words[-1] if words else ""

    def _display_cols(self, main_col: str, max_cols: int = 5) -> list[str]:
        """Pick a sensible set of columns to show in top/bottom results."""
        cols = [main_col]
        for c in self.cat_cols[:2]:
            if c not in cols:
                cols.append(c)
        for c in self.numeric_cols[:3]:
            if c not in cols and len(cols) < max_cols:
                cols.append(c)
        return cols

    @staticmethod
    def _ok(query_type: str, answer: str, data: dict) -> dict:
        return {"query_type": query_type, "answer": answer, "data": data}

    @staticmethod
    def _err(msg: str) -> dict:
        return {"query_type": "error", "answer": msg, "data": {}, "error": msg}
