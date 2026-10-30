"""Cleaning functions for the AI usage dataset.

Every function takes a DataFrame and a `log` list and appends one dict per
decision, so the notebook can show exactly what changed. Nothing is imputed
and no row is removed except exact duplicates. Outliers are flagged; only
values agreed to be impossible (see DEVLOG) are set to NaN, the rest of the
row is kept.
"""
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_FILE = DATA_DIR / "AI_Usage_and_Impact_on_Students_and_Professionals.csv"
CLEAN_FILE = DATA_DIR / "ai_usage_clean.csv"
LOG_FILE = DATA_DIR / "cleaning_log.csv"
MAPPING_FILE = DATA_DIR / "category_mappings.csv"

NUMERIC_TEXT_COLS = [
    "Age",
    "Monthly_Income",
    "AI_Usage_Hours_Per_Day",
    "Monthly_AI_Cost",
    "Time_Saved_Hours_Per_Week",
    "Work_or_Study_Hours_Per_Day",
]

# Raw spelling -> standard value. Keys are matched after strip() only, so every
# observed variant is listed explicitly and the mapping table stays auditable.
CATEGORY_MAPS = {
    "Gender": {
        "Male": "Male", "male": "Male", "MALE": "Male", "M": "Male",
        "Female": "Female", "female": "Female", "FEMALE": "Female", "F": "Female",
        "Other": "Other", "other": "Other", "Non-binary": "Other",
    },
    "AI_Tool": {
        "ChatGPT": "ChatGPT", "chatgpt": "ChatGPT", "Chat GPT": "ChatGPT", "Chatgpt": "ChatGPT",
        "Google Gemini": "Google Gemini", "Gemini": "Google Gemini", "gemini": "Google Gemini",
        "Microsoft Copilot": "Microsoft Copilot", "Copilot": "Microsoft Copilot",
        "copilot": "Microsoft Copilot",
        "Claude": "Claude", "claude": "Claude",
        "Perplexity AI": "Perplexity AI",
        "Grammarly": "Grammarly",
        "Meta AI": "Meta AI",
        "DeepSeek": "DeepSeek",
    },
    # Undergraduate and Bachelor's are kept separate on purpose (see TASK.md).
    "Education_Level": {
        "High School": "High School", "high school": "High School", "HS": "High School",
        "Diploma": "Diploma",
        "Undergraduate": "Undergraduate", "undergrad": "Undergraduate",
        "Bachelor's": "Bachelor's", "Bachelors": "Bachelor's",
        "bachelor's degree": "Bachelor's", "BA/BSc": "Bachelor's",
        "Master's": "Master's", "Masters": "Master's",
        "master's degree": "Master's", "MA/MSc": "Master's",
        "PhD": "PhD", "Ph.D.": "PhD",
    },
    "Country": {
        "India": "India", "india": "India",
        "United States": "United States", "United States of America": "United States",
        "Canada": "Canada", "canada": "Canada",
        "Pakistan": "Pakistan",
        "United Kingdom": "United Kingdom", "U.K.": "United Kingdom",
        "Philippines": "Philippines", "philippines": "Philippines",
        "Brazil": "Brazil", "brazil": "Brazil",
        "Australia": "Australia", "australia": "Australia",
        "Nigeria": "Nigeria",
        "Germany": "Germany",
        "France": "France", "france": "France",
        "Kenya": "Kenya",
    },
}


def load_raw(path=RAW_FILE) -> pd.DataFrame:
    return pd.read_csv(path)


def drop_exact_duplicates(df: pd.DataFrame, log: list) -> pd.DataFrame:
    """Drop rows identical in every column. Also checks that no User_ID is
    shared by rows with different content, which would need a manual decision."""
    deduped = df.drop_duplicates(keep="first")
    leftover_ids = int(deduped["User_ID"].duplicated().sum())
    if leftover_ids:
        raise ValueError(f"{leftover_ids} User_IDs repeat with different content; ask before dropping")
    removed = len(df) - len(deduped)
    log.append({"step": "drop_exact_duplicates", "column": "*", "detail": "exact duplicate rows removed",
                "count": removed})
    return deduped.reset_index(drop=True)


def strip_units(df: pd.DataFrame, cols: list, log: list) -> pd.DataFrame:
    """Remove '$', ',', 'hrs', 'yrs' and whitespace, then convert to float.
    Values that still fail to convert become NaN and are counted."""
    df = df.copy()
    for col in cols:
        raw = df[col].astype("string").str.strip()
        had_unit = raw.str.contains(r"[^\d.\-]", regex=True, na=False)
        stripped = raw.str.replace(r"(?i)\$|,|hrs|yrs|\s", "", regex=True)
        converted = pd.to_numeric(stripped, errors="coerce")
        failed = int((converted.isna() & raw.notna()).sum())
        df[col] = converted.astype("float64")
        log.append({"step": "strip_units", "column": col, "detail": "values with unit/symbol stripped",
                    "count": int(had_unit.sum())})
        log.append({"step": "strip_units", "column": col, "detail": "values that could not be converted",
                    "count": failed})
    return df


def standardize_categories(df: pd.DataFrame, maps: dict, log: list) -> pd.DataFrame:
    """Apply the explicit mapping tables. An unmapped non-null value raises,
    so a new spelling can never slip through silently."""
    df = df.copy()
    for col, mapping in maps.items():
        raw = df[col].astype("string").str.strip()
        unmapped = sorted(set(raw.dropna()) - set(mapping))
        if unmapped:
            raise ValueError(f"{col}: unmapped values {unmapped}")
        before = raw.nunique()
        df[col] = raw.map(mapping)
        changed = int((raw.notna() & (raw != df[col])).sum())
        log.append({"step": "standardize_categories", "column": col,
                    "detail": f"unique values {before} -> {df[col].nunique()}; rows relabeled",
                    "count": changed})
    return df


def mapping_table(maps: dict, df_before: pd.DataFrame) -> pd.DataFrame:
    """Long table of raw -> standard with how many rows had each raw value."""
    rows = []
    for col, mapping in maps.items():
        counts = df_before[col].astype("string").str.strip().value_counts()
        for raw, std in mapping.items():
            rows.append({"column": col, "raw_value": raw, "standard_value": std,
                         "rows": int(counts.get(raw, 0)), "changed": raw != std})
    return pd.DataFrame(rows)


def flag_outliers(df: pd.DataFrame, log: list) -> pd.DataFrame:
    """Add boolean flag columns; no row is removed or altered here."""
    df = df.copy()
    flags = {
        "flag_age_over_80": df["Age"] > 80,
        "flag_usage_over_16h": df["AI_Usage_Hours_Per_Day"] > 16,
        "flag_work_over_24h": df["Work_or_Study_Hours_Per_Day"] > 24,
        "flag_usage_gt_work": df["AI_Usage_Hours_Per_Day"] > df["Work_or_Study_Hours_Per_Day"],
        "flag_saved_gt_weekly_usage": df["Time_Saved_Hours_Per_Week"] > df["AI_Usage_Hours_Per_Day"] * 7,
        "flag_income_extreme": df["Monthly_Income"] > df["Monthly_Income"].quantile(0.75) * 10,
    }
    numeric = df[[c for c in NUMERIC_TEXT_COLS] + ["Productivity_Score", "Accuracy_Rating", "Satisfaction_Score"]]
    flags["flag_negative_value"] = (numeric < 0).any(axis=1)
    for name, mask in flags.items():
        df[name] = mask.fillna(False).astype(bool)
        log.append({"step": "flag_outliers", "column": name, "detail": "rows flagged (not removed)",
                    "count": int(df[name].sum())})
    return df


# flag column -> column whose value is set to NaN (decision 2026-10-30, DEVLOG)
IMPOSSIBLE_VALUES = {
    "flag_age_over_80": "Age",
    "flag_usage_over_16h": "AI_Usage_Hours_Per_Day",
    "flag_income_extreme": "Monthly_Income",
}


def null_impossible_values(df: pd.DataFrame, log: list) -> pd.DataFrame:
    """Set flagged impossible values to NaN; the row and its flag stay."""
    df = df.copy()
    for flag, col in IMPOSSIBLE_VALUES.items():
        mask = df[flag]
        df.loc[mask, col] = float("nan")
        log.append({"step": "null_impossible_values", "column": col,
                    "detail": f"values set to NaN where {flag}", "count": int(mask.sum())})
    return df


def clean(df_raw: pd.DataFrame):
    """Full pipeline. Returns (clean_df, log_df, mapping_df)."""
    log = []
    log.append({"step": "load", "column": "*", "detail": "raw rows", "count": len(df_raw)})
    df = drop_exact_duplicates(df_raw, log)
    mappings = mapping_table(CATEGORY_MAPS, df)
    df = strip_units(df, NUMERIC_TEXT_COLS, log)
    df = standardize_categories(df, CATEGORY_MAPS, log)
    df = flag_outliers(df, log)
    df = null_impossible_values(df, log)
    log.append({"step": "done", "column": "*", "detail": "clean rows", "count": len(df)})
    return df, pd.DataFrame(log), mappings


def run_checks(df_raw: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """Automated post-cleaning checks. Returns a table with pass/fail per check."""
    numeric_cols = NUMERIC_TEXT_COLS + ["Productivity_Score", "Accuracy_Rating", "Satisfaction_Score"]
    expected_missing = df_raw.drop_duplicates()[numeric_cols].isna().sum()
    for flag, col in IMPOSSIBLE_VALUES.items():
        expected_missing[col] += int(df[flag].sum())
    checks = [
        ("no exact duplicate rows", int(df.duplicated().sum()) == 0),
        ("User_ID unique", df["User_ID"].is_unique),
        ("row count = raw - exact duplicates", len(df) == len(df_raw) - int(df_raw.duplicated().sum())),
        ("numeric columns are numeric", all(pd.api.types.is_numeric_dtype(df[c]) for c in numeric_cols)),
        ("NaN only from raw + nulled impossible values", (df[numeric_cols].isna().sum() == expected_missing).all()),
        ("no impossible values left", not ((df["Age"] > 80) | (df["AI_Usage_Hours_Per_Day"] > 16)
                                           | (df["Work_or_Study_Hours_Per_Day"] > 24)).any()),
        ("Gender in {Male, Female, Other}", set(df["Gender"].dropna()) <= {"Male", "Female", "Other"}),
        ("AI_Tool unique = 8", df["AI_Tool"].nunique() == 8),
        ("Education_Level unique = 6", df["Education_Level"].nunique() == 6),
        ("Country unique = 12", df["Country"].nunique() == 12),
        ("User_Type unique = 2", df["User_Type"].nunique() == 2),
        ("AI_Purpose unique = 8", df["AI_Purpose"].nunique() == 8),
        ("no negative numeric values", not (df[numeric_cols] < 0).any().any()),
    ]
    return pd.DataFrame(checks, columns=["check", "passed"])


def before_after_summary(df_raw: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df_raw.columns:
        rows.append({
            "column": col,
            "dtype_before": str(df_raw[col].dtype), "dtype_after": str(df[col].dtype),
            "unique_before": df_raw[col].nunique(), "unique_after": df[col].nunique(),
            "missing_before": int(df_raw[col].isna().sum()), "missing_after": int(df[col].isna().sum()),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    raw = load_raw()
    cleaned, log_df, map_df = clean(raw)
    cleaned.to_csv(CLEAN_FILE, index=False)
    log_df.to_csv(LOG_FILE, index=False)
    map_df.to_csv(MAPPING_FILE, index=False)
    print(log_df.to_string(index=False))
    print(run_checks(raw, cleaned).to_string(index=False))
