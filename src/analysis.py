def filter_data(df, year, sex=None):
    data = df[df["annee"] == year].copy()
    if sex is not None and "sexe" in data.columns:
        data = data[data["sexe"] == sex].copy()
    return data

def rank_regions(df):
    d = df.sort_values("taux_chomage", ascending=False).copy()
    d["rang"] = range(1, len(d) + 1)
    return d

def get_summary(df, focus_region="Tanger-Tétouan-Al Hoceïma"):
    average = df["taux_chomage"].mean()
    max_row = df.loc[df["taux_chomage"].idxmax()]
    min_row = df.loc[df["taux_chomage"].idxmin()]
    focus = df[df["region"] == focus_region]
    return average, max_row, min_row, focus


def get_ranking(df, year, sex=None):
    """Return regions ranked by unemployment rate for a selected year."""
    data = df[df["annee"] == year].copy()
    if sex is not None and "sexe" in data.columns:
        data = data[data["sexe"] == sex].copy()
    data = data.dropna(subset=["taux_chomage"])
    data = data.sort_values("taux_chomage", ascending=False).copy()
    data["rang"] = range(1, len(data) + 1)
    return data


def get_summary_stats(df, year, sex=None):
    """Compute dashboard KPI values for a selected year."""
    data = get_ranking(df, year, sex)
    if data.empty:
        return {
            "moyenne_nationale": 0,
            "valeur_max": 0,
            "region_max": "Donnée non disponible",
            "valeur_min": 0,
            "region_min": "Donnée non disponible",
        }

    max_row = data.loc[data["taux_chomage"].idxmax()]
    min_row = data.loc[data["taux_chomage"].idxmin()]
    return {
        "moyenne_nationale": round(float(data["taux_chomage"].mean()), 1),
        "valeur_max": round(float(max_row["taux_chomage"]), 1),
        "region_max": max_row["region"],
        "valeur_min": round(float(min_row["taux_chomage"]), 1),
        "region_min": min_row["region"],
    }


def compare_regions(df, region, baseline="National", sex=None):
    """Return a wide table comparing one region to the national/baseline series over time."""
    data = df.copy()
    if sex is not None and "sexe" in data.columns:
        data = data[data["sexe"] == sex].copy()

    selected = data[data["region"] == region][["annee", "taux_chomage"]].rename(
        columns={"taux_chomage": region}
    )

    if baseline in data["region"].unique():
        base = data[data["region"] == baseline][["annee", "taux_chomage"]].rename(
            columns={"taux_chomage": baseline}
        )
    else:
        base = data.groupby("annee", as_index=False)["taux_chomage"].mean().rename(
            columns={"taux_chomage": baseline}
        )

    out = selected.merge(base, on="annee", how="outer").sort_values("annee")
    return out


def get_region_rank_over_time(df, region, sex=None):
    """Return the rank of a region for every year. Rank 1 means highest unemployment rate."""
    rows = []
    years = sorted(df["annee"].dropna().unique())
    for year in years:
        ranking = get_ranking(df, year, sex)
        match = ranking[ranking["region"] == region]
        if not match.empty:
            rows.append({
                "annee": year,
                "rang": int(match["rang"].iloc[0]),
                "taux_chomage": float(match["taux_chomage"].iloc[0]),
            })
    import pandas as pd
    return pd.DataFrame(rows)

