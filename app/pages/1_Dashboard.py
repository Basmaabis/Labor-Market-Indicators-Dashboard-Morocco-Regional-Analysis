
import os
import sys

import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from dashboard_lib import (
    available_indicators,
    available_years,
    header_html,
    load_css,
    load_data,
    ranking_bar,
    regional_data,
    style_ranking_table,
    summary,
)
st.set_page_config(page_title="Dashboard", layout="wide")
st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)
st.markdown(header_html("TABLEAU DE BORD DES INDICATEURS DU MARCHÉ DU TRAVAIL", "Classement et indicateurs clés par région"), unsafe_allow_html=True)

df = load_data()
indicators = available_indicators(df)

if not indicators:
    st.error("Aucun indicateur exploitable n'a été trouvé dans le fichier de données.")
    st.stop()


c1, c2 = st.columns(2)
with c1:
    indicator = st.selectbox("Indicateur", indicators)
years = available_years(df, indicator)
if not years:
    st.error(f"Aucune donnée disponible pour l'indicateur {indicator}.")
    st.stop()
with c2:
    year = st.selectbox("Année", years)

data = regional_data(df, int(year), indicator)
stats = summary(data)

m1, m2, m3 = st.columns(3)
m1.metric("Moyenne des régions", f"{stats['moyenne']:.1f}%")
m2.metric("Taux le plus élevé", f"{stats['max_value']:.1f}%", stats["max_region"])
m3.metric("Taux le plus faible", f"{stats['min_value']:.1f}%", stats["min_region"])

left, right = st.columns([1.4, 1])
with left:
    st.plotly_chart(ranking_bar(data, indicator, int(year)), use_container_width=True)
with right:
    st.dataframe(
        style_ranking_table(data).style.format({"Taux (%)": "{:.1f}", "Écart à la moyenne": "{:+.1f}"}),
        use_container_width=True,
        hide_index=True,
    )


