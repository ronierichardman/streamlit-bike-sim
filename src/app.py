import simulation as sim
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_echarts import st_echarts


# def main():
#     sim_ergebnisse = run_simulation(3)

# if __name__ == "__main__":
#     main()

def display_tabular_data(sim_ergebnisse):
    # Tabellarische Darstellung der Ergebnisse
    st.subheader("Maximaler Monatsgewinn und Treffer")
    for i, sim_ergebnis in enumerate(sim_ergebnisse):
        with st.expander(f"Durchlauf {i + 1}"):
            df = pd.DataFrame(columns=["Experiment", "Jahresgewinn", "Treffer Quote"])
            for exp, jahresergebnis in enumerate(sim_ergebnis):
                df.loc[exp] = [exp] + jahresergebnis.to_list()
            st.dataframe(df, use_container_width=True, hide_index=True)


# def analyze(sim_ergebnisse):
#     # ergebnis = {}
#     # ergebnis = statistic.rechnen(sim_ergebnisse)
#     # for ergebnis in sim_ergebnisse:
#     pass


# def plot(sim_ergebnisse):
#     st.subheader("Gewinnverlauf über das Jahr (monatlich)")
#     fig, ax = plt.subplots()

#     for ergebnis in sim_ergebnisse:
#         plt.plot(ergebnis.monatsergebnisse, label=f"Monat {ergebnis.monat}")

#     plt.xlabel("Monate")
#     plt.ylabel("Gewinn")
#     plt.title("Simulationsergebnisse")
#     plt.legend()
#     plt.show()

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

##----------------------- Hauptprogramm: Streamlit App --------------------------------------
# Titel
st.set_page_config(page_title="Bike-Verleihstationen", page_icon="🚲")
st.title("Monte Carlo Simulation")
st.header("Bike-Verleihstationen in Dresden 🚲")
# Eingabefelder
preis_pro_stunde = st.number_input("Preis pro Stunde (€):", min_value=1.0, max_value=10.0, value=5.0, step=0.5)
ort = st.selectbox("Ort:", ["Ganz Dresden", "Altstadt", "Neustadt", "Südvorstadt"])
durchlaeufe = st.number_input("Anzahl der Durchläufe:", min_value=1, max_value=40, value=10, step=1)
# Button für die Simulation
if st.button("Simulation starten"):
    with st.spinner("Simulation läuft..."):
        try:
            sim_ergebnisse = run_simulation(durchlaeufe, preis_pro_stunde, ort)
            display_tabular_data(sim_ergebnisse)
            st.success("Simulation abgeschlossen!")
            st.balloons()
        except Exception as e:
            print(f"Fehler bei der Simulation: {e}")
            st.error("Fehler bei der Simulation: " + str(e))

# option = {
#     "xAxis": {
#         "type": "category",
#         "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
#     },
#     "yAxis": {"type": "value"},
#     "series": [{"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "line"}],
# }
# st_echarts(
#     options=option, height="400px",
# )



