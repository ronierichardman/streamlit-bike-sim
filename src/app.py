import simulation as sim
from data import Ortvariablen
# import statistic as stat
from statistic import DurchlaufErgebnis
import streamlit as st
# from streamlit_echarts import st_echarts
import numpy as np
import pandas as pd
import time
import applogger

logger = applogger.get_logger(__name__)

 
def display_tabular_data(durchlauf_ergebnisse: list[DurchlaufErgebnis]):
    # Tabellarische Darstellung der Ergebnisse
    st.subheader("Jahresgewinn und Trefferquote")
    for i, durchlauf_ergebnis in enumerate(durchlauf_ergebnisse):
        with st.expander(f"Durchlauf {i + 1}"):
            df = pd.DataFrame(columns=["Experiment", "Jahresgewinn (€)", "Trefferquote (%)"])
            for exp, jahresergebnis in enumerate(durchlauf_ergebnis.jahresergebnisse):
                df.loc[exp] = [exp + 1] + jahresergebnis.to_list()
            st.dataframe(df, use_container_width=True, hide_index=True)


# def analyze(sim_ergebnisse):
#     # ergebnis = {}
#     # ergebnis = statistic.rechnen(sim_ergebnisse)
#     # for ergebnis in sim_ergebnisse:
#     pass


def plot_simulation(durchlauf_ergebnisse):
    #Diagramm für die Simulationsergebnisse
    # stat.plot_diagram_durchlaeufe(durchlauf_ergebnisse)
    pass


def run_simulation(durchlaeufen=10, preis_pro_stunde=5, ort="Ganz Dresden"):
    sim_ergebnisse = []
    for i in range(durchlaeufen):
        sim_ergebnis = sim.run_monte_carlo(preis_pro_stunde=preis_pro_stunde, ort=ort)  
        sim_ergebnisse.append(sim_ergebnis)
        print(f"Durchlauf {i + 1}:")
        for i, jahr in enumerate(sim_ergebnis):
            print(i + 1)
            print(jahr)

    return sim_ergebnisse

def run_simulation_func(func, num_durchlaeufen=10, preis_pro_stunde=5, ort="Ganz Dresden"):
    durchlauf_ergebnisse = []
    for i in range(num_durchlaeufen):
        sim_ergebnis = func(preis_pro_stunde=preis_pro_stunde, ort=ort)
        durchlauf_ergebnisse.append(DurchlaufErgebnis(sim_ergebnis))
    return durchlauf_ergebnisse


def run_simulation_2(num_durchlaeufen, preis_pro_stunde=0, ort=""):
    durchlauf_ergebnisse = []
    for i in range(num_durchlaeufen):
        sim_ergebnis = sim.run_monte_carlo()
        durchlauf_ergebnis = DurchlaufErgebnis(sim_ergebnis)
        durchlauf_ergebnisse.append(durchlauf_ergebnis)
        print(f"Durchlauf {i + 1}:")
        for i, jahr in enumerate(sim_ergebnis):
            print(i + 1)
            print(jahr)

    return durchlauf_ergebnisse

def main():
    # start_time = time.time()
    # sim_ergebnisse = run_simulation_func(sim.run_monte_carlo)
    # end_time = time.time()
    # elapsed_time = end_time - start_time
    # print(f"New Simulation completed in {elapsed_time:.2f} seconds.")

    ##----------------------- Hauptprogramm: Streamlit App --------------------------------------
    # Titel
    st.set_page_config(page_title="Bike-Verleihstationen", page_icon="🚲")
    st.title("Monte Carlo Simulation")
    st.header("Bike-Verleihstationen in Dresden 🚲")
    # Eingabefelder
    preis_pro_stunde = st.number_input("Preis pro Stunde (€):", min_value=1.0, max_value=10.0, value=5.0, step=0.5)
    ort = st.selectbox("Ort:", Ortvariablen.ALL_NAMES, index=0)
    durchlaeufe = st.number_input("Anzahl der Durchläufe:", min_value=1, max_value=40, value=10, step=1)
    # Button für die Simulation
    if st.button("Simulation starten"):
        with st.spinner("Simulation läuft..."):
            try:
                start_time = time.time()
                sim_ergebnisse = run_simulation_func(sim.run_monte_carlo, durchlaeufe, preis_pro_stunde, ort)
                end_time = time.time()
                elapsed_time = end_time - start_time
                st.success(f"Simulation abgeschlossen in {elapsed_time:.2f} Sekunden!")

                display_tabular_data(sim_ergebnisse)
                # plot_simulation(sim_ergebnisse)
                st.balloons()
            except Exception as e:
                logger.error(f"Fehler bei der Simulation ({e.__cause__}): {e}")
                st.error("Fehler bei der Simulation: " + str(e))
                

if __name__ == "__main__":
    main()
