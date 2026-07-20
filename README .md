# 📊 Labor Market Indicators Dashboard
### Kingdom of Morocco — Regional Analysis

*A visualization tool developed within the Tangier-Tétouan-Al Hoceïma Regional Directorate (DRTTA)*

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)](https://plotly.com)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![License](https://img.shields.io/badge/License-Internal%20use-lightgrey)](#-license)
[![Status](https://img.shields.io/badge/Status-In%20development-yellow)](#)

[Context](#-context) • [Features](#-features) • [Installation](#-quick-start) • [Structure](#️-project-structure) • [Author](#-author)

</div>

---

## 🎯 Context

This project was born during my internship at the **Haut-Commissariat au Plan (HCP)**, Tangier-Tétouan-Al Hoceïma Regional Directorate. My supervisor gave me read-only access to their **National Employment Survey (ENE)** database, with no specific requirements. **On my own initiative**, I identified a real need at the DRTTA (visually exploring a database that had only ever been consulted via spreadsheet) and independently designed, developed, and delivered a complete application to **visualize and compare Morocco's 12 regions** across four key labor market indicators.

> 💡 **The idea**: give the DRTTA a concrete tool to explore their own database, spot regional trends faster, and detect potential flaws — missing values, suspicious gaps, series breaks — that would otherwise go unnoticed in a raw spreadsheet.

### 🏆 What this project demonstrates

- **Initiative and autonomy**: an unrequested project, identified and carried through end-to-end without technical supervision, from needs analysis to delivery of a functional tool.
- **Business understanding**: translating complex statistical indicators (unemployment, underemployment, activity, employment) into visualizations usable by non-data specialists.
- **Data rigor**: cleaning, structuring, and validating a real-world database (ENE), including detection of missing values and inconsistencies.
- **Applied technical skills**: designing a clear architecture (separation of business logic / interface), full-stack Python development (data processing → visualization → deployable web interface).
- **Product sense**: six complementary, synchronized views designed for real use by a regional directorate, not just as a technical demo.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🗺️ **Interactive choropleth map** | Morocco's 12 regions, colored according to the selected indicator's value |
| 📈 **Time comparison** | Track 1 to 3 regions side by side, year by year |
| 🏆 **Regional ranking** | Regions sorted by indicator, with deviation from the national average |
| 🔥 **Regions × years heatmap** | Overview to spot trends and anomalies |
| 🕸️ **Comparative radar** | Multi-indicator comparison between regions |
| 🔍 **Regional focus** | Dedicated page for Tangier-Tétouan-Al Hoceïma |

All views are **synchronized**: changing the indicator or year in the sidebar updates the entire dashboard.

---

## 📐 Available indicators

| Indicator | Description |
|---|---|
| Unemployment rate | Share of the labor force without a job |
| Employment rate | Share of the working-age population holding a job |
|  Underemployment rate | Share of employed workers working fewer hours than normal, or under inadequate conditions |
|  Activity rate | Share of the working-age population that is active (employed or seeking employment) |

---



## 🏗️ Architecture

The application is structured into **three independent layers**, allowing data, business logic, or interface to evolve separately without breaking everything:



### Layer details

| Layer | Role | Related files |
|---|---|---|
| **1. Data sources & processing** | ENE ingestion, cleaning, transformation, aggregation, and validation with Pandas, joined with the GeoJSON of the 12 regions | `notebooks/`, `data/processed/`, `data/geo/` |
| **2. Back-end — Business logic** | Data access (CSV/GeoJSON loading, caching), calculations (indicators, aggregations, time comparisons, deviations), and chart generation (maps, series, heatmap, radar, rankings) | `src/dashboard_lib.py` |
| **3. Application — Streamlit** | User interface (filters, region selection, navigation), application pages (main dashboard, regional focus), and state/interactivity management | `app/app.py`, `app/pages/`, `app/assets/` |
| **4. Visualizations & features** | Final result exposed to the user: choropleth map, time comparison, regional ranking, heatmap, comparative radar, regional focus | Rendered in the Streamlit interface |

This separation between **business logic and interface** is a deliberate choice: it allows, for example, reusing `dashboard_lib.py` in an analysis notebook or a future API, without depending on Streamlit.

---

## 🚀 Quick start

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Basmaabis/regional-unemployment-dashboard.git
cd regional-unemployment-dashboard

# 2. Create and activate the virtual environment
python -m venv env
env\Scripts\activate        # Windows
# source env/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
streamlit run app/app.py
```

The application opens automatically at [http://localhost:8501](http://localhost:8501).

---

## 🗂️ Project structure

```
regional-unemployment-dashboard/
├── app/
│   ├── app.py                 # Streamlit entry point
│   ├── pages/                 # Secondary pages (Dashboard, Regional focus)
│   └── assets/                # Logos, style.css
├── src/
│   └── dashboard_lib.py       # Business logic: data, maps, charts
├── data/
│   ├── processed/              # Cleaned data (CSV)
│   └── geo/                    # GeoJSON of Morocco's regions
├── notebooks/                  # Exploration and cleaning notebooks
├── docs/                        # Additional documentation, screenshots
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech stack

- **[Streamlit](https://streamlit.io)** — interactive web interface
- **[Python](https://www.python.org)** 3.10+
- **[Pandas](https://pandas.pydata.org)** — data processing, cleaning, and aggregation
- **[Plotly](https://plotly.com)** — choropleth maps, heatmaps, radars, time series
- **[GeoPandas](https://geopandas.org)** — geospatial data handling (regional GeoJSON)
- **[Altair](https://altair-viz.github.io)** — supplementary visualizations
- **[NumPy](https://numpy.org)** — numerical computations
- **GeoJSON** — geographic boundaries of Morocco's 12 regions

---

## 📚 Data source

**Haut-Commissariat au Plan (HCP)** — Tangier-Tétouan-Al Hoceïma Regional Directorate
National Employment Survey (ENE)

---

## 👩‍💻 Author

**Basma Abis**
Engineering student — Software and Intelligent Systems (LSI) track
Faculty of Sciences and Techniques of Tangier — Abdelmalek Essaâdi University

Full design, development, and deployment of the project — from analyzing the DRTTA's needs to the final application : carried out independently as part of an internship at the HCP.

📧 [pcdebasma@gmail.com](mailto:pcdebasma@gmail.com) · [GitHub](https://github.com/Basmaabis)
