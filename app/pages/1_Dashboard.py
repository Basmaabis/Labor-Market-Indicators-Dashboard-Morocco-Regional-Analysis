
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
    ranking_table_html,
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


c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    indicator = st.selectbox("Indicateur", indicators)
years = available_years(df, indicator)
if not years:
    st.error(f"Aucune donnée disponible pour l'indicateur {indicator}.")
    st.stop()
with c2:
    year = st.selectbox("Années", years)
with c3:
    regions = sorted(df.loc[~df["is_national"], "region"].dropna().unique())
    selected_regions = st.multiselect("Régions à surligner", regions, default=regions[:2], max_selections=min(2, len(regions)))

data = regional_data(df, int(year), indicator)
stats = summary(data)

m1, m2, m3 = st.columns(3)
m1.metric("Moyenne des régions", f"{stats['moyenne']:.1f}%")
m2.metric("Taux le plus élevé", f"{stats['max_value']:.1f}%", stats["max_region"])
m3.metric("Taux le plus faible", f"{stats['min_value']:.1f}%", stats["min_region"])

left, right = st.columns([1.4, 1])
with left:
    st.plotly_chart(ranking_bar(data, indicator, int(year), selected_regions), use_container_width=True)
with right:
    st.markdown(ranking_table_html(data, selected_regions), unsafe_allow_html=True)


