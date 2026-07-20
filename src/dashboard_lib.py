from __future__ import annotations

import base64
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "taux_chomage_regions_clean.csv"
GEOJSON_PATH = ROOT / "data" / "geo" / "morocco_regions.geojson"
ASSETS = ROOT / "app" / "assets"

TITLE = "#1F2937"
SECONDARY = "#374151"
BORDER = "#E5E7EB"
GRID = "#E5E7EB"
PAGE_BG = "#F8FAFC"
CARD_BG = "#FFFFFF"
DATA_FOCUS = "#C47C5A"
SERIES_COLORS = ["#800020", "#F18A2B", "#C47C5A", "#A7B18A", "#4A6670"]
MAP_SCALE = ["#E8E2D5", "#C9BFA8", "#9FC5C1", "#6D8A96", "#4A6670"]
HEATMAP_SCALE = ["#EAF1FA", "#BBD3EA", "#7FA8D2", "#4A78AE", "#1F4E86"]
FOCUS_REGION = "Tanger-Tétouan-Al Hoceïma"

REGION_COORDS = {
    "Tanger-Tétouan-Al Hoceïma": (35.35, -5.55),
    "Oriental": (34.50, -2.30),
    "Fès-Meknès": (33.90, -4.80),
    "Rabat-Salé-Kénitra": (34.20, -6.20),
    "Béni Mellal-Khénifra": (32.40, -6.40),
    "Casablanca-Settat": (33.10, -7.60),
    "Marrakech-Safi": (31.60, -8.30),
    "Drâa-Tafilalet": (31.20, -5.40),
    "Souss-Massa": (30.20, -9.30),
    "Régions du Sud": (26.80, -12.00),
}

INDICATORS = {
    "Taux de chômage": "taux_chomage",
    "Taux d'emploi": "taux_emploi",
    "Taux de sous-emploi": "taux_sous_emploi",
    "Activité": "taux_activite",
}

REGION_FIXES = {}

GEOJSON_REGION_FIXES = {}


def load_regions_geojson() -> dict:
    with GEOJSON_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def header_html(title: str, subtitle: str = "") -> str:
    fst = image_data_uri(ASSETS / "logo_fstt.png")
    hcp = image_data_uri(ASSETS / "logo_hcp.png")
    left = f'<img class="logo-left" src="{fst}" alt="Logo FST Tanger">' if fst else "<div></div>"
    right = f'<img class="logo-right" src="{hcp}" alt="Logo HCP">' if hcp else "<div></div>"
    return f"""
    <div class="app-header">
      {left}
      <div class="app-header-main">
        <div class="app-header-title">{title}</div>
        <div class="app-header-subtitle">{subtitle}</div>
      </div>
      {right}
    </div>
    """


def load_css() -> str:
    css = ASSETS / "style.css"
    return css.read_text(encoding="utf-8") if css.exists() else ""


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, encoding="utf-8")
    df["region"] = df["region"].replace(REGION_FIXES)
    df["annee"] = pd.to_numeric(df["annee"], errors="coerce").astype("Int64")
    for col in ["taux_chomage", "taux_emploi", "taux_sous_emploi", "taux_activite"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "is_national" not in df.columns:
        df["is_national"] = df["region"].eq("National")
    return df


def available_indicators(df: pd.DataFrame) -> list[str]:
    return [label for label, col in INDICATORS.items() if col in df.columns and df[col].notna().any()]


def available_years(df: pd.DataFrame, indicator_label: str) -> list[int]:
    col = value_column(indicator_label)
    if col not in df.columns:
        return []
    years = pd.to_numeric(df.loc[df[col].notna(), "annee"], errors="coerce").dropna().astype(int)
    return sorted(years.unique().tolist(), reverse=True)


def value_column(indicator_label: str) -> str:
    return INDICATORS[indicator_label]


def regional_data(df: pd.DataFrame, year: int, indicator: str) -> pd.DataFrame:
    col = value_column(indicator)
    data = df[(df["annee"] == year) & (~df["is_national"])].copy()
    data = data.dropna(subset=[col])
    data["valeur"] = data[col]
    data = data.sort_values("valeur", ascending=False).reset_index(drop=True)
    data["rang"] = data.index + 1
    data["ecart_moyenne"] = data["valeur"] - data["valeur"].mean()
    return data


def summary(data: pd.DataFrame, focus_region: str = FOCUS_REGION) -> dict:
    if data.empty:
        return {
            "moyenne": 0,
            "max_region": "N/D",
            "max_value": 0,
            "min_region": "N/D",
            "min_value": 0,
            "focus_value": None,
            "focus_rank": None,
        }
    max_row = data.loc[data["valeur"].idxmax()]
    min_row = data.loc[data["valeur"].idxmin()]
    focus = data[data["region"] == focus_region]
    return {
        "moyenne": float(data["valeur"].mean()),
        "max_region": max_row["region"],
        "max_value": float(max_row["valeur"]),
        "min_region": min_row["region"],
        "min_value": float(min_row["valeur"]),
        "focus_value": None if focus.empty else float(focus["valeur"].iloc[0]),
        "focus_rank": None if focus.empty else int(focus["rang"].iloc[0]),
    }


def clean_plot(fig):
    fig.update_layout(
        font=dict(family="Inter, Segoe UI, sans-serif", color=TITLE, size=12),
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        margin=dict(l=24, r=24, t=70, b=36),
        title=dict(font=dict(size=18, color=TITLE), x=0.02, xanchor="left"),
        legend=dict(orientation="v", bgcolor="rgba(255,255,255,0.92)", font=dict(color=SECONDARY)),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID, griddash="dot", zeroline=False, title_font_color=SECONDARY, tickfont_color=SECONDARY)
    fig.update_yaxes(showgrid=False, zeroline=False, title_font_color=SECONDARY, tickfont_color=SECONDARY, automargin=True)
    return fig


def ranking_bar(data: pd.DataFrame, indicator: str, year: int):
    chart = data.sort_values("valeur", ascending=True).copy()
    fig = px.bar(
        chart,
        x="valeur",
        y="region",
        orientation="h",
        color="valeur",
        color_continuous_scale=MAP_SCALE,
        text=chart["valeur"].map(lambda v: f"{v:.1f}%"),
        hover_data={"region": True, "valeur": ":.1f", "rang": True},
        title=f"Classement régional - {indicator} ({year})",
        labels={"valeur": "Taux (%)", "region": ""},
    )
    fig.update_traces(textposition="outside", marker_line_width=0, cliponaxis=False)
    fig.update_layout(height=500)
    focus_mask = chart["region"].eq(FOCUS_REGION).tolist()
    fig.update_traces(marker_line_color=[DATA_FOCUS if is_focus else "rgba(0,0,0,0)" for is_focus in focus_mask], marker_line_width=[3 if is_focus else 0 for is_focus in focus_mask])
    return clean_plot(fig)


def comparison_bar(df: pd.DataFrame, regions: list[str], indicator: str):
    col = value_column(indicator)
    data = df[(df["region"].isin(regions)) & (~df["is_national"])].copy().dropna(subset=[col])
    fig = px.bar(
        data,
        x="annee",
        y=col,
        color="region",
        barmode="group",
        color_discrete_sequence=SERIES_COLORS,
        text=data[col].map(lambda v: f"{v:.1f}%"),
        title="Comparaison temporelle des régions sélectionnées",
        labels={"annee": "Année", col: "Taux (%)", "region": "Région"},
        hover_data={col: ":.1f"},
    )
    fig.update_traces(textposition="outside", marker_line_width=0, cliponaxis=False)
    fig.update_layout(height=560)
    return clean_plot(fig)


def evolution_line(df: pd.DataFrame, indicator: str, selected_regions: list[str] | None = None):
    col = value_column(indicator)
    data = df.dropna(subset=[col]).copy()
    if selected_regions:
        data = data[data["region"].isin(selected_regions + ["National"])]
    fig = px.line(
        data,
        x="annee",
        y=col,
        color="region",
        markers=True,
        title=f"Évolution temporelle - {indicator}",
        labels={"annee": "Année", col: "Taux (%)", "region": "Région"},
        color_discrete_sequence=SERIES_COLORS,
        hover_data={col: ":.1f"},
    )
    fig.update_layout(height=540)
    for trace in fig.data:
        if trace.name == "National":
            trace.line.dash = "dash"
            trace.line.width = 3
            trace.line.color = "#A7B18A"
        elif trace.name == FOCUS_REGION:
            trace.line.width = 4
            trace.line.color = DATA_FOCUS
        else:
            trace.line.width = 2
            trace.opacity = 0.82
    return clean_plot(fig)


def schematic_map(data: pd.DataFrame, indicator: str, year: int):
    geojson = load_regions_geojson()
    map_df = data.copy()

    fig = px.choropleth(
        map_df,
        geojson=geojson,
        locations="region",
        featureidkey="properties.region",
        color="valeur",
        color_continuous_scale=MAP_SCALE,
        hover_name="region",
        hover_data={"valeur": ":.1f", "rang": True, "region": False},
        title=f"Carte régionale - {indicator} ({year})",
        labels={"valeur": "Taux (%)"},
    )
    fig.update_traces(
        marker_line_color="#FFFFFF",
        marker_line_width=1.1,
        selector=dict(type="choropleth"),
    )
    fig = clean_plot(fig)
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        showcountries=False,
        showcoastlines=False,
        showland=False,
        showframe=False,
        bgcolor=CARD_BG,
    )
    fig.update_layout(
        height=620,
        margin=dict(l=10, r=10, t=70, b=10),
        geo=dict(bgcolor=CARD_BG),
        coloraxis_colorbar=dict(
            title=dict(text="Taux (%)", font=dict(color=TITLE, size=14)),
            tickfont=dict(color=TITLE, size=12),
            len=0.72,
            y=0.48,
        ),
    )
    return fig


def heatmap_year_region(df: pd.DataFrame, indicator: str):
    col = value_column(indicator)
    data = df[~df["is_national"]].pivot_table(index="region", columns="annee", values=col, aggfunc="mean").sort_index()
    fig = px.imshow(data, color_continuous_scale=HEATMAP_SCALE, aspect="auto", text_auto=".1f", title=f"Heatmap régions x années - {indicator}", labels=dict(color="Taux (%)"))
    return clean_plot(fig)


def radar_chart(df: pd.DataFrame, year: int, regions: list[str]):
    available = available_indicators(df)
    if len(available) < 2:
        return None
    rows = []
    for region in regions:
        row = {"region": region}
        subset = df[(df["annee"] == year) & (df["region"] == region)]
        for label in available:
            col = value_column(label)
            row[label] = None if subset.empty else subset[col].iloc[0]
        rows.append(row)
    fig = go.Figure()
    for index, row in enumerate(rows):
        values = [row[label] for label in available]
        fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=available + [available[0]], fill="toself", name=row["region"], line=dict(color=SERIES_COLORS[index % len(SERIES_COLORS)])))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), title=f"Radar comparatif - {year}")
    return clean_plot(fig)


def style_ranking_table(data: pd.DataFrame):
    view = data[["rang", "region", "valeur", "ecart_moyenne"]].copy()
    return view.rename(columns={"rang": "Rang", "region": "Région", "valeur": "Taux (%)", "ecart_moyenne": "Écart à la moyenne"})






