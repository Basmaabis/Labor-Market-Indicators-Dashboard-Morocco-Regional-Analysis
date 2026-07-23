
import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from dashboard_lib import (
    FOCUS_REGION,
    available_indicators,
    available_years,
    clean_plot,
    evolution_line,
    header_html,
    load_css,
    load_data,
    regional_data,
    schematic_map,
    style_ranking_table,
    summary,
    value_column,
)

st.set_page_config(page_title="Focus région", layout="wide")
st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)
st.markdown(header_html("TABLEAU DE BORD DES INDICATEURS DU MARCHÉ DU TRAVAIL", "Focus régional : Tanger-Tétouan-Al Hoceïma"), unsafe_allow_html=True)

df = load_data()
indicators = available_indicators(df)

if not indicators:
    st.error("Aucun indicateur exploitable n'a été trouvé dans le fichier de données.")
    st.stop()
regions = sorted(df.loc[~df["is_national"], "region"].dropna().unique())


c1, c2 = st.columns([1, 1])
with c1:
    indicator = st.selectbox("Indicateur", indicators)
years = available_years(df, indicator)
if not years:
    st.error(f"Aucune donnée disponible pour l'indicateur {indicator}.")
    st.stop()
with c2:
    year = st.selectbox("Année", years)

data_year = regional_data(df, int(year), indicator)
stats = summary(data_year, FOCUS_REGION)

k1, k2, k3 = st.columns(3)
k1.metric("Valeur régionale", "N/D" if stats["focus_value"] is None else f"{stats['focus_value']:.1f}%")
k2.metric("Rang régional", "N/D" if stats["focus_rank"] is None else f"{stats['focus_rank']}")
k3.metric("Moyenne des régions", f"{stats['moyenne']:.1f}%")

left, right = st.columns([1.1, 1])
with left:
    with st.container(border=True):
        st.plotly_chart(schematic_map(data_year, indicator, int(year)), use_container_width=True)
with right:
    with st.container(border=True):
        position_data = data_year.sort_values("valeur", ascending=True)
        position_fig = px.bar(
            position_data,
            x="valeur",
            y="region",
            orientation="h",
            color=position_data["region"].eq(FOCUS_REGION),
            color_discrete_map={True: "#C47C5A", False: "#D6E7E4"},
            title=f"Position nationale - {year}",
            labels={"valeur": "Taux (%)", "region": "", "color": ""},
        )
        position_fig.update_layout(showlegend=False)
        st.plotly_chart(clean_plot(position_fig), use_container_width=True)

with st.container(border=True):
    st.plotly_chart(evolution_line(df, indicator, [FOCUS_REGION]), use_container_width=True)

with st.container(border=True):
    st.subheader("Classement détaillé")
    st.dataframe(
        style_ranking_table(data_year).style.format({"Taux (%)": "{:.1f}", "Écart à la moyenne": "{:+.1f}"}),
        use_container_width=True,
        hide_index=True,
    )





