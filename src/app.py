import simulation as sim
import statistic as stat
from statistic import DurchlaufErgebnis
import streamlit as st
import numpy as np
import pandas as pd
from streamlit_echarts import st_echarts

 
def display_tabular_data(sim_ergebnisse):
    # Tabellarische Darstellung der Ergebnisse
    st.subheader("Maximaler Monatsgewinn und Treffer")
    for i, sim_ergebnis in enumerate(sim_ergebnisse):
        with st.expander(f"Durchlauf {i + 1}"):
            df = pd.DataFrame(columns=["Experiment", "Gewinn", "Treffer"])
            for exp, jahresergebnis in enumerate(sim_ergebnis):
                df.loc[exp] = [exp] + jahresergebnis.to_list()
            st.dataframe(df, use_container_width=True, hide_index=True)


# def analyze(sim_ergebnisse):
#     # ergebnis = {}
#     # ergebnis = statistic.rechnen(sim_ergebnisse)
#     # for ergebnis in sim_ergebnisse:
#     pass


def plot_simulation(durchlauf_ergebnisse):
    #Diagramm für die Simulationsergebnisse
    stat.plot_diagram_durchlaeufe(durchlauf_ergebnisse)
    stat.plot_diagram_max_gewinn_im_monat(durchlauf_ergebnisse)
    stat.plot_diagram_durchschnittliche_gewinn_im_monat(durchlauf_ergebnisse)
    stat.plot_diagram_min_gewinn_im_monat(durchlauf_ergebnisse)


def run_simulation(durchlaeufen, preis_pro_stunde=0, ort=""):
    sim_ergebnisse = []
    for i in range(durchlaeufen):
        sim_ergebnis = sim.run_monte_carlo()
        sim_ergebnisse.append(sim_ergebnis)
        print(f"Durchlauf {i + 1}:")
        for i, jahr in enumerate(sim_ergebnis):
            print(i + 1)
            print(jahr)

    return sim_ergebnisse

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

def display_statistics(sim_ergebnisse):
    results=stat.rechnen_durchlaeufe(sim_ergebnisse)
    #tabellarische Darstellung der Ergebnisse
    st.subheader("Statistik der Simulationsergebnisse")
    df = pd.DataFrame(columns=["Mittelwert", "Standardabweichung", "Median","Oberes Quartil", "Unteres Quartil","T Verteilung Gamma Fraktil","KI obere Grenze","KI untere Grenze"])
    df.loc[0] = [results.jahresgewinn, results.jahresgewinn_std, results.jahresgewinn_median, results.jahresgewinn_oberes_quartil, results.jahresgewinn_unteres_quartil, results.jahresgewinn_t_verteilung_gamma_fraktil, results.jahresdewinn_ki_high, results.jahresdewinn_ki_low]
    st.dataframe(df, use_container_width=True, hide_index=True)
 


##----------------------- Hauptprogramm: Streamlit App --------------------------------------
# Titel
st.set_page_config(page_title="Bike-Verleihstationen", page_icon="🚲")
st.title("Monte Carlo Simulation")
st.header("Bike-Verleihstationen in Dresden 🚲")
# Eingabefelder
preis_pro_stunde = st.number_input("Preis pro Stunde (€):", min_value=1.0, max_value=10.0, value=5.0, step=0.5)
ort = st.selectbox("Ort:", ["Ganz Dresden", "Altstadt", "Neustadt", "Südvorstadt"])
durchlaeufe = st.number_input("Anzahl der Durchläufe:", min_value=1, max_value=30, value=10, step=1)
# Button für die Simulation
if st.button("Simulation starten"):
    with st.spinner("Simulation läuft..."):
        try:
            #sim_ergebnisse = run_simulation(durchlaeufe, preis_pro_stunde, ort)
            #display_tabular_data(sim_ergebnisse)
            sim_ergebnisse = run_simulation_2(durchlaeufe, preis_pro_stunde, ort)
            display_statistics(sim_ergebnisse)
            plot_simulation(sim_ergebnisse)
            st.success("Simulation abgeschlossen!")
            st.balloons()
        except Exception as e:
            print(f"Fehler bei der Simulation: {e}")
            st.error("Fehler bei der Simulation: " + str(e))


# def main():
#     sim_ergebnisse = run_simulation_2(3)
#     plot_simulation(sim_ergebnisse)

# if __name__ == "__main__":
#     main()
