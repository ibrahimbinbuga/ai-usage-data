"""Ham veri doğrulama raporu (Adım 2). Çıktı: data/raw_report.csv + stdout."""
import sys
from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "data" / "AI_Usage_and_Impact_on_Students_and_Professionals.csv"


def raw_report(df: pd.DataFrame) -> pd.DataFrame:
    """Sütun bazında tip, eksik, benzersiz ve sayısala çevrilebilirlik özeti."""
    rows = []
    for col in df.columns:
        s = df[col]
        nonnull = s.dropna()
        as_num = pd.to_numeric(nonnull, errors="coerce")
        rows.append({
            "column": col,
            "dtype": str(s.dtype),
            "missing": int(s.isna().sum()),
            "missing_pct": round(s.isna().mean() * 100, 1),
            "unique": int(s.nunique()),
            "non_numeric_values": int(as_num.isna().sum()),
            "numeric_min": as_num.min(),
            "numeric_max": as_num.max(),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = pd.read_csv(RAW)
    pd.set_option("display.width", 200, "display.max_columns", 20, "display.max_rows", 200)
    print("shape:", df.shape)
    rep = raw_report(df)
    print(rep.to_string(index=False))
    print("\nexact duplicate rows (keep=first):", int(df.duplicated().sum()))
    print("duplicated User_ID (keep=first):", int(df["User_ID"].duplicated().sum()))
    dup_ids = df[df["User_ID"].duplicated(keep=False)]
    print("rows sharing a User_ID:", len(dup_ids), "| of which are not exact dups:",
          int((~dup_ids.duplicated(keep=False)).sum()))
    print("total missing cells:", int(df.isna().sum().sum()))
    print("rows with any missing:", int(df.isna().any(axis=1).sum()))
    rep.to_csv(RAW.parent / "raw_report.csv", index=False)
