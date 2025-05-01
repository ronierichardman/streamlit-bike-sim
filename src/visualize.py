
from data import Monatsvariablen, Wetterlagen, VARKOSTEN_PRO_STUNDE
from models import StatistikErgebnis
from statistic import BoxplotData
import streamlit as st
from streamlit_echarts import st_echarts
import pandas as pd
import numpy as np

def display_tabular(stat_ergebnis: StatistikErgebnis):
    st.subheader("Jahresgewinn und Trefferquote")
    st.markdown(f"Maximaler Jahresgewinn: **{round(stat_ergebnis.max_jahresergebnis.gewinn):,} €** -- Trefferquote: **{stat_ergebnis.max_jahresergebnis.trefferquote():.2f} %**")
    st.markdown(f"Durchschnittlicher Jahresgewinn: **{round(stat_ergebnis.mw_jahresgewinn):,} €** -- Durchschnittliche Trefferquote: **{stat_ergebnis.mw_trefferquote:.2f} %**")
   
    for i, durchlauf_ergebnis in enumerate(stat_ergebnis.durchlauf_ergebnisse):
        with st.expander(f"Durchlauf {i + 1}"):
            df = pd.DataFrame(columns=["Experiment", "Jahresgewinn", "Maximaler Monatsgewinn","Maximaler Tagesgewinn", "Trefferquote (%)"])
            for exp, jahresergebnis in enumerate(durchlauf_ergebnis.jahresergebnisse):
                df.loc[exp] = [exp + 1] + jahresergebnis.to_list()
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"Durchschnittlicher Jahresgewinn:  &emsp;{round(durchlauf_ergebnis.mw_jahresgewinn()):,} €" )
            st.caption(f"Durchschnittlicher Monatsgewinn:  &emsp;{round(durchlauf_ergebnis.mw_monatsgewinn()):,} €" )
            st.caption(f"Durchschnittlicher Tagesgewinn:   &emsp;{round(durchlauf_ergebnis.mw_tagesgewinn()):,} €" )


def plot_max_profit_a_run(stat_ergebnis: StatistikErgebnis):
    st.subheader("Höchster Jahresgewinn in jedem einzelnen Durchlauf")
    x = Monatsvariablen.ALL_NAMES
    series = []
    max_durchlauf = min(stat_ergebnis.durchlaufanzahl, 5)

    max_jahresergebnis = stat_ergebnis.max_jahresergebnis
    max_jahresergebnisse = [d.max_jahresergebnis() for d in stat_ergebnis.durchlauf_ergebnisse if d.max_jahresergebnis() != max_jahresergebnis]
    for j in max_jahresergebnisse[:max_durchlauf]:
        series.append({
            "name": "Andere",
            "type": "line",
            "smooth": True,
            "data": [round(m.gewinn) for m in j.monatsergebnisse()]
        })
    series.append({
        "name": "Max. Jahresgewinn",
        "type": "line",
        "smooth": True,
        "data": [round(m.gewinn) for m in max_jahresergebnis.monatsergebnisse()]
    })
    option = {
        "tooltip": { "trigger": "axis" },
        "legend": {
            "data": ["Max. Jahresgewinn", "Andere"]
        },
        "xAxis": {"type": "category", "boundaryGap": False, "data": x},
        "yAxis": { "type": "value" },
        "series": series
    }
    st_echarts(options=option, height="500px")
    st.caption(f"Aus Darstellungsgründen sind nur die Durchlauf von maximalen Jahresgewinn und die ersten {max_durchlauf} Durchläufe berücksichtigt.")


def plot_profit_by_month(stat_ergebnis: StatistikErgebnis):
    st.subheader("Monatliche Gewinne: Höchst-, Durchschnitts- und Tiefstwerte aus allen Durchläufen")
    x = Monatsvariablen.ALL_NAMES
    max_gewinne = [ round(stat_ergebnis.max_monatsergebnis(i).gewinn) for i in range(12)]
    mw_gewinne = [ round(stat_ergebnis.mw_monatsgewinn(i)) for i in range(12) ]
    min_gewinne = [ round(stat_ergebnis.min_monatsergebnis(i).gewinn) for i in range(12) ]
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
    st.caption(f"Summe der Monatsmaximalwerte:&emsp;{sum(max_gewinne):,} €")
    st.caption(f"Summe der Monatsmittelwerte:&emsp; {sum(mw_gewinne):,} €")
    st.caption(f"Summe der Monatsminimalwerte:&emsp;{sum(min_gewinne):,} €")


def plot_profit_by_day(stat_ergebnis: StatistikErgebnis):
    st.subheader("Verteilung der besten Tagesgewinne pro Jahr")
    max_gewinne = [ t.gewinn for t in stat_ergebnis.max_tagesergebnisse ]
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
    st.subheader("Median, Streuung, Ausreißer der Tagesgewinne")
    labels = [f"{i+1}." for i in range(stat_ergebnis.durchlaufanzahl)]
    boxplot_data = [ d.boxplot_data().to_list() for d in stat_ergebnis.durchlauf_ergebnisse ]
    option = {
        "title": {"text": "Boxplot der Tagesgewinne"},
        "tooltip": {
            "trigger": "item", 
            "axisPointer": {"type": "shadow"},
            },
        "xAxis": {
            "type": "category",
            "data": labels,
            "boundaryGap": True,
            "nameGap": 30,
            "splitArea": {"show": False}
        },
        "yAxis": {
            "type": "value",
            "name": "Gewinn",
            "splitArea": {"show": True}
        },
        "series": [{
            "name": "Gewinn",
            "type": "boxplot",
            "data": boxplot_data,
            "itemStyle": {"color": "#4dabf7"}
        }]
    }
    st_echarts(options=option, height="500px")
    st.caption("Wie stabil oder schwankend sind die täglichen Gewinne?") 
    # Damit sieht man auf einen Blick, ob viele Verluste oder viele sichere Tage existieren. Volatiles oder stabiles Geschäft?

def boxplot_profit_by_weather(stat_ergebnis: StatistikErgebnis):
    st.subheader("Wetter vs. Tagesgewinn")
    sonnig_data = [t.gewinn for t in stat_ergebnis.tagesergebnisse if t.wetter == Wetterlagen.SONNIG]
    bewoelkt_data = [t.gewinn for t in stat_ergebnis.tagesergebnisse if t.wetter == Wetterlagen.BEWOELKT]
    regen_data = [t.gewinn for t in stat_ergebnis.tagesergebnisse if t.wetter == Wetterlagen.REGEN]
    
    boxplot_data = [
        BoxplotData(sonnig_data).to_list(), 
        BoxplotData(bewoelkt_data).to_list(), 
        BoxplotData(regen_data).to_list()
    ]
    option = {
        "title": {"text": "Boxplot der Tagesgewinne nach Wetter"},
        "tooltip": {
            "trigger": "item", 
            "axisPointer": {"type": "shadow"},
            },
        "xAxis": {
            "type": "category",
            "data": Wetterlagen.ALL_NAMES
        },
        "yAxis": {
            "type": "value",
            "name": "Gewinn"
        },
        "series": [{
            "name": "Gewinn",
            "type": "boxplot",
            "data": boxplot_data,
            "itemStyle": {"color": "#4dabf7"}
        }]
    }
    st_echarts(options=option, height="500px")

def display_statistics(stat_ergebnis: StatistikErgebnis):
    st.subheader("Statistiken")
    st.caption(f"• Ort: {stat_ergebnis.ort.name}, Einwohner: {stat_ergebnis.ort.einwohner:,}")
    st.caption(f"• Variante Kosten pro Stunde: {VARKOSTEN_PRO_STUNDE} €")
    st.caption(f"• Fixkosten pro Tag: {stat_ergebnis.ort.fixkosten_pro_tag} €")

    data = [
        ["Durchschnittliche Kundenzahl pro Tag", f"{stat_ergebnis.ci_tageskundenzahl.mw:.2f} Kunde", f"{stat_ergebnis.ci_tageskundenzahl.ci_str}"],
        ["Durchnschnittlicher Gewinn pro Tag", f"{round(stat_ergebnis.ci_tagesgewinn.mw):,} €", f"{stat_ergebnis.ci_tagesgewinn.ci_str}"],
        ["Durchschnittlicher Gewinn pro Monat", f"{round(stat_ergebnis.ci_monatsgewinn().mw):,} €", f"{stat_ergebnis.ci_monatsgewinn().ci_str}"],
        ["Durchschnittlicher Gewinn pro Jahr", f"{round(stat_ergebnis.ci_jahresgewinn.mw):,} €", f"{stat_ergebnis.ci_jahresgewinn.ci_str}"],
        ["Durchschnittlicher Trefferquote", f"{stat_ergebnis.ci_trefferquote.mw:.2f} %", f"{stat_ergebnis.ci_trefferquote.ci_str}"],      
    ]
    data = pd.DataFrame(data, columns=["Kennzahl", "Ergebnis", "Konfidenzintervalle (95%)"])
    st.dataframe(data, use_container_width=True, hide_index=True)

    data_case = [
        ["Besten Tagesgewinn", f"{round(stat_ergebnis.max_tagesergebnis.gewinn):,} €", f"{stat_ergebnis.max_tagesergebnis.monat.monat_name}, {stat_ergebnis.max_tagesergebnis.temperatur:.2f} \N{DEGREE SIGN}C, {stat_ergebnis.max_tagesergebnis.wetter.name}, {stat_ergebnis.max_tagesergebnis.wochentag.name}"],
        ["Schlechtesten Tagesgewinn", f"{round(stat_ergebnis.min_tagesergebnis.gewinn):,} €", f"{stat_ergebnis.min_tagesergebnis.monat.monat_name}, {stat_ergebnis.min_tagesergebnis.temperatur:.2f} \N{DEGREE SIGN}C, {stat_ergebnis.min_tagesergebnis.wetter.name}, {stat_ergebnis.min_tagesergebnis.wochentag.name}"]   
    ]
    data_case = pd.DataFrame(data_case, columns=["Kennzahl", "Ergebnis", "Details"])
    st.dataframe(data_case, use_container_width=True, hide_index=True)
