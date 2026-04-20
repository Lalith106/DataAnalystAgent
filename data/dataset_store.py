import pandas as pd

df_store = None

def set_df(df):
    global df_store
    df_store = df

def get_df():
    return df_store

def clear_df():
    global df_store
    df_store = None

def generate_summary(df: pd.DataFrame) -> dict:
    """
    Returns a structured summary dictionary for the uploaded dataset.
    """
    summary = {}

    # ── Basic shape ──────────────────────────────────────────────
    summary["rows"] = len(df)
    summary["columns"] = len(df.columns)
    summary["total_cells"] = df.size
    summary["missing_cells"] = int(df.isnull().sum().sum())
    summary["missing_pct"] = round(summary["missing_cells"] / summary["total_cells"] * 100, 1) if summary["total_cells"] else 0
    summary["duplicate_rows"] = int(df.duplicated().sum())

    # ── Column categories ────────────────────────────────────────
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    summary["numeric_cols"] = numeric_cols
    summary["categorical_cols"] = categorical_cols
    summary["datetime_cols"] = datetime_cols

    # ── Numeric statistics ───────────────────────────────────────
    num_stats = []
    for col in numeric_cols[:10]:
        s = df[col].dropna()
        if len(s) == 0:
            continue
        num_stats.append({
            "column": col,
            "min": round(float(s.min()), 4),
            "max": round(float(s.max()), 4),
            "mean": round(float(s.mean()), 4),
            "median": round(float(s.median()), 4),
            "std": round(float(s.std()), 4),
            "nulls": int(df[col].isnull().sum()),
        })
    summary["numeric_stats"] = num_stats

    # ── Categorical top values ───────────────────────────────────
    cat_stats = []
    for col in categorical_cols[:8]:
        vc = df[col].value_counts()
        cat_stats.append({
            "column": col,
            "unique": int(df[col].nunique()),
            "top": str(vc.index[0]) if len(vc) else "—",
            "top_freq": int(vc.iloc[0]) if len(vc) else 0,
            "nulls": int(df[col].isnull().sum()),
        })
    summary["cat_stats"] = cat_stats

    # ── Date range ───────────────────────────────────────────────
    date_ranges = []
    for col in datetime_cols:
        s = df[col].dropna()
        if len(s):
            date_ranges.append({
                "column": col,
                "min": str(s.min()),
                "max": str(s.max()),
            })
    summary["date_ranges"] = date_ranges

    return summary
