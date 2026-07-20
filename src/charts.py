import plotly.graph_objects as go

DATA_FOCUS = "#C47C5A"
DATA_LIGHT = "#D6E7E4"
REGION_HIGHLIGHT = "Tanger-Tétouan-Al Hoceïma"


def bar_ranking(ranking_df):
    colors = [DATA_FOCUS if r == REGION_HIGHLIGHT else DATA_LIGHT for r in ranking_df["region"]]
    fig = go.Figure(go.Bar(
        x=ranking_df["taux_chomage"],
        y=ranking_df["region"],
        orientation="h",
        marker_color=colors,
        text=ranking_df["taux_chomage"].astype(str) + "%",
        textposition="outside",
        cliponaxis=False,
    ))
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Taux de chômage (%)",
        yaxis_title=None,
        font=dict(color="#1F2937"),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=16, r=24, t=24, b=24),
        height=400,
    )
    return fig


def evolution_line(evolution_df, label=REGION_HIGHLIGHT):
    fig = go.Figure(go.Scatter(
        x=evolution_df["annee"],
        y=evolution_df["taux_chomage"],
        mode="lines+markers",
        line=dict(color="#800020", width=3),
        name=label,
    ))
    fig.update_layout(
        yaxis_title="Taux de chômage (%)",
        xaxis_title=None,
        font=dict(color="#1F2937"),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=16, r=24, t=24, b=24),
        height=300,
    )
    return fig
