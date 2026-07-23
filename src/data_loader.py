from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    from .cleaning import PROCESSED_PATH, build_clean_csv, normalize_region
except ImportError:  # Allows `python src/data_loader.py` and Streamlit sys.path imports.
    from cleaning import PROCESSED_PATH, build_clean_csv, normalize_region

NUMERIC_COLUMNS = ["taux_chomage", "taux_emploi", "taux_sous_emploi", "taux_activite"]


def load_data(path: Path = PROCESSED_PATH, rebuild_if_missing: bool = True) -> pd.DataFrame:
    """Load the clean dashboard CSV, rebuilding it from raw Excel files if needed."""
    if not path.exists():
        if not rebuild_if_missing:
            raise FileNotFoundError(path)
        build_clean_csv(path)

    df = pd.read_csv(path, encoding="utf-8")
    df["region"] = df["region"].map(normalize_region)
    df = df.dropna(subset=["region"])
    df["annee"] = pd.to_numeric(df["annee"], errors="coerce").astype("Int64")
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "is_national" not in df.columns:
        df["is_national"] = df["region"].eq("National")
    else:
        df["is_national"] = df["is_national"].astype(str).str.lower().isin(["true", "1", "yes", "oui"])
    return df


if __name__ == "__main__":
    print(load_data().head())

