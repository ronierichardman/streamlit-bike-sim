from data import Monatsvariablen
from models import DurchlaufErgebnis, StatistikErgebnis
import streamlit as st
from streamlit_echarts import st_echarts
import pandas as pd
import numpy as np

def display_tabular(stat_ergebnis: StatistikErgebnis):
    st.subheader("Jahresgewinn und Trefferquote")
    st.markdown(f"Durchschnittlicher Jahresgewinn: {round(stat_ergebnis.mw_jahresgewinn):,} €")
    st.markdown(f"Durchschnittlicher Trefferquote: {stat_ergebnis.mw_trefferquote:.2f} %")
    for i, durchlauf_ergebnis in enumerate(stat_ergebnis.durchlauf_ergebnisse):
        with st.expander(f"Durchlauf {i + 1}"):
            df = pd.DataFrame(columns=["Experiment", "Jahresgewinn (€)", "Maximaler Monatsgewinn (€)","Maximaler Tagesgewinn (€)", "Trefferquote (%)"])
            for exp, jahresergebnis in enumerate(durchlauf_ergebnis.jahresergebnisse):
                df.loc[exp] = [exp + 1] + jahresergebnis.to_list()
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown(f"**Maximaler Jahresgewinn:** &emsp;{round(durchlauf_ergebnis.max_jahresergebnis().gewinn):,} €" )
            st.markdown(f"**Durchschn. Jahresgewinn:**  &emsp;{round(durchlauf_ergebnis.mw_jahresgewinn()):,} €" )
            st.markdown(f"**Minimaler Jahresgewinn:** &emsp;{round(durchlauf_ergebnis.min_jahresergebnis().gewinn):,} €" )


def plot_max_profit_a_run(durchlauf_ergebnisse: list[DurchlaufErgebnis]):
    st.subheader("Höchster Jahresgewinn in jedem einzelnen Durchlauf")
    x = Monatsvariablen.ALL_NAMES
    series = []
    max_durchlauf = min(len(durchlauf_ergebnisse), 10)
    for i, durchlauf_ergebnis in enumerate(durchlauf_ergebnisse[:max_durchlauf]):
        series.append({
            "name": f"Durchlauf {i + 1}",
            "type": "line",
            "smooth": True,
            "data": [round(m.gewinn) for m in durchlauf_ergebnis.max_jahresergebnis().monatsergebnisse()]
        })
    option = {
        "tooltip": { "trigger": "axis" },
        "xAxis": {"type": "category", "boundaryGap": False, "data": x},
        "yAxis": { "type": "value" },
        "series": series
    }
    st_echarts(options=option, height="500px")
    st.caption("Aus Darstellungsgründen sind nur die ersten 10 Durchläufe berücksichtigt.")

def plot_profit_by_month(stat_ergebnis: StatistikErgebnis):
    st.subheader("Monatliche Gewinne: Höchst-, Durchschnitts- und Tiefstwerte aus allen Durchläufen")
    x = Monatsvariablen.ALL_NAMES
    max_gewinne = [ round(stat_ergebnis.max_monatsergebnis(i).gewinn) for i in range(12)]
    mw_gewinne = [ round(stat_ergebnis.mw_monatsgewinn(i)) for i in range(12) ]
    min_gewinne = [ round(stat_ergebnis.min_monatsergebnis(i).gewinn) for i in range(12) ]
    # max_gewinne = [ round(d.max_monatsergebnis(m).gewinn) for d in stat_ergebnis.durchlauf_ergebnisse for m in range(12) ]
    # min_gewinne = [ round(d.min_monatsergebnis(m).gewinn) for d in stat_ergebnis.durchlauf_ergebnisse for m in range(12) ]
    # mw_gewinne = [ round(d.mw_monatsgewinn(m)) for d in stat_ergebnis.durchlauf_ergebnisse for m in range(12) ]
    option = {
        "tooltip": { "trigger": "axis" },
        "legend": {
            "data": ["Maximaler Gewinn", "Durchschn. Gewinn", "Minimaler Gewinn"]
        },
        "xAxis": {"type": "category", "boundaryGap": False, "data": x},
        "yAxis": { "type": "value" },
        "series": [
            {   
                "name": "Maximaler Gewinn",
                "data": max_gewinne,
                "type": "line",
                "smooth": True
            },
            {   
                "name": "Durchschn. Gewinn",
                "data": mw_gewinne,
                "type": "line",
                "smooth": True
            },
            {   
                "name": "Minimaler Gewinn",
                "data": min_gewinne,
                "type": "line",
                "smooth": True
            }
        ]
    }
    st_echarts(options=option, height="500px")
    st.markdown(f"**Summe der Monatsmaximalwerte:**&emsp;{sum(max_gewinne):,} €")
    st.markdown(f"**Summe der Monatsmittelwerte:**&emsp; {sum(mw_gewinne):,} €")
    st.markdown(f"**Summe der Monatsminimalwerte:**&emsp;{sum(min_gewinne):,} €")


def plot_profit_by_day(stat_ergebnis: StatistikErgebnis):
    st.subheader("Verteilung der besten Tagesgewinne pro Jahr")
    max_gewinne = [ t.gewinn for t in stat_ergebnis.max_tagesergebnisse ]
    # max_gewinne = [t.gewinn for d in stat_ergebnis.durchlauf_ergebnisse for t in d.max_tagesergebnisse()]
    counts, bins = np.histogram(max_gewinne, bins=20)
    option = {
        "title": {"text": "Histogramm der maximalen Tagesgewinne"},
        "tooltip": { "trigger": "axis" },
        "xAxis": {
        "type": "category",
        "data": [f"{int(bins[i])}-{int(bins[i+1])}" for i in range(len(bins)-1)],
        "axisLabel": {"rotate": 45}
        },
        "yAxis": {"type": "value"},
        "series": [{
            "data": counts.tolist(),
            "type": "bar",
            "color": "skyblue",
            "barWidth": "60%",
        }]
    }
    st_echarts(options=option, height="500px")
    st.caption("Wie häufig kommt ein sehr hoher Gewinn vor?")


def boxplot_profit_by_day(stat_ergebnis: StatistikErgebnis):
    st.subheader("Boxplot der Tagesgewinne pro Jahr")
