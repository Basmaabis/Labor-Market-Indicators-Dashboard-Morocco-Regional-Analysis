from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_PATH = ROOT / "data" / "processed" / "taux_chomage_regions_clean.csv"
CHOMAGE_FILE = RAW_DIR / "taux_chomage_sexe_region_2015-2025.xlsx"
EMPLOI_FILE = RAW_DIR / "taux_emploi_regions.xlsx"
SOUS_EMPLOI_FILE = RAW_DIR / "taux_sous_emploi_regions.xlsx"
ACTIVITE_FILE = RAW_DIR / "taux_activite_regions.csv"

REGION_FIXES = {
    "tanger tetouan al hoceima": "Tanger-Tétouan-Al Hoceïma",
    "tanger tetouan hoceima": "Tanger-Tétouan-Al Hoceïma",
    "oriental": "Oriental",
    "fes meknes": "Fès-Meknès",
    "rabat sale kenitra": "Rabat-Salé-Kénitra",
    "beni mellal khenifra": "Béni Mellal-Khénifra",
    "casablanca settat": "Casablanca-Settat",
    "marrakech safi": "Marrakech-Safi",
    "draa tafilalet": "Drâa-Tafilalet",
    "souss massa": "Souss-Massa",
    "regions du sud": "Régions du Sud",
    "national": "National",
    "ensemble": "National",
}

OUTPUT_COLUMNS = [
    "annee",
    "region",
    "taux_chomage",
    "is_national",
    "taux_emploi",
    "taux_sous_emploi",
    "taux_activite",
]
EXPECTED_REGIONS = {
    "Tanger-Tétouan-Al Hoceïma",
    "Oriental",
    "Fès-Meknès",
    "Rabat-Salé-Kénitra",
    "Béni Mellal-Khénifra",
    "Casablanca-Settat",
    "Marrakech-Safi",
    "Drâa-Tafilalet",
    "Souss-Massa",
    "Régions du Sud",
    "National",
}


def _key(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    text = text.replace("â€™", "'").strip().lower()
    text = re.sub(r"\s+", " ", text)
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.replace("'", " ")
    return re.sub(r"[^a-z0-9]+", " ", ascii_text).strip()


def normalize_region(value: object) -> str | None:
    text = "" if pd.isna(value) else str(value).strip()
    if not text:
        return None
    return REGION_FIXES.get(_key(text), text)


def _numeric(value: object) -> float | None:
    if pd.isna(value):
        return None
    if isinstance(value, str):
        value = value.replace("%", "").replace(",", ".").replace("\t", "").strip()
    return pd.to_numeric(value, errors="coerce")


def _require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Source introuvable: {path}")


def clean_chomage(path: Path = CHOMAGE_FILE) -> pd.DataFrame:
    _require_file(path)
    raw = pd.read_excel(path, sheet_name=0, header=None)
    if raw.shape[0] < 3 or raw.shape[1] < 4:
        raise ValueError(f"Structure inattendue dans {path.name}: au moins 3 lignes et 4 colonnes attendues")

    header_keys = [_key(value) for value in raw.iloc[1, :3].tolist()]
    if "region" not in header_keys:
        raise ValueError(f"Colonne Région absente dans {path.name}")
    if "sexe" not in header_keys:
        raise ValueError(f"Colonne Sexe absente dans {path.name}")

    year_columns: dict[int, int] = {}
    for col_index, value in raw.iloc[0].items():
        year = pd.to_numeric(value, errors="coerce")
        if pd.notna(year):
            year_columns[col_index] = int(year)
    if not year_columns:
        raise ValueError(f"Aucune colonne année détectée dans {path.name}")

    rows = []
    for _, row in raw.iloc[2:].iterrows():
        region = normalize_region(row.iloc[1] if len(row) > 1 else None)
        sexe = str(row.iloc[2]).strip().lower() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
        if not region or sexe != "total":
            continue
        for col_index, year in year_columns.items():
            value = _numeric(row.iloc[col_index])
            if pd.notna(value):
                rows.append({"annee": year, "region": region, "taux_chomage": float(value)})

    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError(f"Aucune donnée chômage exploitable trouvée dans {path.name}")
    missing = EXPECTED_REGIONS.difference(set(df["region"].unique()))
    if missing:
        raise ValueError(f"Régions attendues absentes dans {path.name}: {sorted(missing)}")
    return df


def clean_long_indicator(path: Path, output_column: str) -> pd.DataFrame:
    _require_file(path)
    if path.suffix.lower() == ".csv":
        raw = pd.read_csv(path, encoding="utf-8-sig")
    else:
        raw = pd.read_excel(path, sheet_name=0)

    raw.columns = [str(col).replace("\t", "").strip() for col in raw.columns]
    column_map = {_key(col): col for col in raw.columns}
    required = {"regions": "Regions", "annee": "Année", "valeur": "Valeur"}
    missing = [label for key, label in required.items() if key not in column_map]
    if missing:
        raise ValueError(f"Colonnes manquantes dans {path.name}: {missing}")

    df = raw.loc[:, [column_map["regions"], column_map["annee"], column_map["valeur"]]].copy()
    df.columns = ["Regions", "Année", "Valeur"]
    for col in ["Regions", "Valeur"]:
        df[col] = df[col].astype(str).str.replace("\t", "", regex=False).str.strip()
    df["region"] = df["Regions"].map(normalize_region)
    df["annee"] = pd.to_numeric(df["Année"], errors="coerce")
    df[output_column] = df["Valeur"].map(_numeric)
    df = df.dropna(subset=["region", "annee", output_column])
    df["annee"] = df["annee"].astype(int)
    df[output_column] = df[output_column].astype(float)
    return df[["annee", "region", output_column]]


def merge_sources(
    chomage_path: Path = CHOMAGE_FILE,
    emploi_path: Path = EMPLOI_FILE,
    sous_emploi_path: Path = SOUS_EMPLOI_FILE,
    activite_path: Path = ACTIVITE_FILE,
) -> pd.DataFrame:
    chomage = clean_chomage(chomage_path)
    emploi = clean_long_indicator(emploi_path, "taux_emploi")
    sous_emploi = clean_long_indicator(sous_emploi_path, "taux_sous_emploi")
    activite = clean_long_indicator(activite_path, "taux_activite")

    merged = chomage.merge(emploi, on=["annee", "region"], how="left")
    merged = merged.merge(sous_emploi, on=["annee", "region"], how="left")
    merged = merged.merge(activite, on=["annee", "region"], how="left")
    merged["is_national"] = merged["region"].eq("National")
    merged = merged.sort_values(["region", "annee"]).reset_index(drop=True)
    return merged[OUTPUT_COLUMNS]


def build_clean_csv(output_path: Path = PROCESSED_PATH) -> pd.DataFrame:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = merge_sources()
    df.to_csv(output_path, index=False, encoding="utf-8")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Fusionne les sources HCP en un CSV propre pour le dashboard.")
    parser.add_argument("--output", type=Path, default=PROCESSED_PATH, help="Chemin du CSV de sortie.")
    args = parser.parse_args()
    df = build_clean_csv(args.output)
    print(f"CSV généré: {args.output}")
    print(f"Lignes: {len(df)}")
    print(df.groupby("annee")[["taux_chomage", "taux_emploi", "taux_sous_emploi", "taux_activite"]].count())


if __name__ == "__main__":
    main()

