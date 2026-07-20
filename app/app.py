
import os
import sys

import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from dashboard_lib import (
    FOCUS_REGION,
    available_indicators,
    available_years,
    comparison_bar,
    evolution_line,
    heatmap_year_region,
    header_html,
    load_css,
    load_data,
    radar_chart,
    ranking_bar,
    regional_data,
    schematic_map,
    style_ranking_table,
    summary,
)

st.set_page_config(page_title="Indicateurs du marché du travail", layout="wide")
st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)
st.markdown(header_html("TABLEAU DE BORD DES INDICATEURS DU MARCHÉ DU TRAVAIL", "Analyse comparative des régions marocaines à partir des données ENE du Haut-Commissariat au Plan"), unsafe_allow_html=True)

df = load_data()
indicators = available_indicators(df)


if not indicators:
    st.error("Aucun indicateur exploitable n'a été trouvé dans le fichier de données.")
    st.stop()

with st.container(border=True):
    f1, f2, f3 = st.columns([1.25, 1, 2.2])
    with f1:
        indicator = st.selectbox("Choisir un indicateur", indicators)
    years = available_years(df, indicator)
    if not years:
        st.error(f"Aucune donnée disponible pour l'indicateur {indicator}.")
        st.stop()
    with f2:
        year = st.selectbox("Choisir une année", years)
    with f3:
        regions = sorted(df.loc[~df["is_national"], "region"].dropna().unique())
        default = regions.index(FOCUS_REGION) if FOCUS_REGION in regions else 0
        selected_regions = st.multiselect(
            "Comparer des régions",
            regions,
            default=[regions[default], regions[0] if regions[0] != regions[default] else regions[min(1, len(regions) - 1)]],
            max_selections=3,
        )

if len(indicators) < 3:
    st.info(
        "Le sélecteur est prêt pour trois indicateurs, mais le fichier actuel contient uniquement les colonnes disponibles. "
        "Ajoutez taux_emploi et taux_sous_emploi au CSV pour activer les vues multi-indicateurs."
    )

data_year = regional_data(df, int(year), indicator)
stats = summary(data_year)
radar = radar_chart(df, int(year), selected_regions or [FOCUS_REGION])

k1, k2, k3, k4 = st.columns(4)
k1.metric("Moyenne des régions", f"{stats['moyenne']:.1f}%")
k2.metric("Taux le plus élevé", f"{stats['max_value']:.1f}%", stats["max_region"])
k3.metric("Taux le plus faible", f"{stats['min_value']:.1f}%", stats["min_region"])
focus_label = "N/D" if stats["focus_value"] is None else f"{stats['focus_value']:.1f}%"
focus_delta = None if stats["focus_rank"] is None else f"Rang {stats['focus_rank']}"
k4.metric("Tanger-Tétouan-Al Hoceïma", focus_label, focus_delta)

st.markdown(" ")
with st.container(border=True):
    st.plotly_chart(comparison_bar(df, selected_regions or [FOCUS_REGION], indicator), use_container_width=True)

ranking_left, ranking_right = st.columns([1.25, 0.85])
with ranking_left:
    with st.container(border=True):
        st.plotly_chart(ranking_bar(data_year, indicator, int(year)), use_container_width=True)
with ranking_right:
    with st.container(border=True):
        st.subheader(f"Classement régional - {year}")
        table = style_ranking_table(data_year)
        st.dataframe(
            table.style.format({"Taux (%)": "{:.1f}", "Écart à la moyenne": "{:+.1f}"}),
            use_container_width=True,
            hide_index=True,
        )

with st.container(border=True):
    st.plotly_chart(evolution_line(df, indicator, selected_regions), use_container_width=True)

with st.container(border=True):
    st.plotly_chart(heatmap_year_region(df, indicator), use_container_width=True)

map_col, radar_col = st.columns([1, 1])
with map_col:
    with st.container(border=True):
        st.plotly_chart(schematic_map(data_year, indicator, int(year)), use_container_width=True)
with radar_col:
    with st.container(border=True):
        if radar is not None:
            st.plotly_chart(radar, use_container_width=True)
        else:
            st.markdown(
                "<div class='info-card'><span class='badge'>Radar</span><br><br>"
                "Le graphique radar sera activé lorsque le fichier contiendra au moins deux indicateurs "
                "par région, par exemple taux de chômage et taux d'emploi.</div>",
                unsafe_allow_html=True,
            )


