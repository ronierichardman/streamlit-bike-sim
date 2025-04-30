import simulation as sim
from models import DurchlaufErgebnis, StatistikErgebnis
from data import Stationen
import visualizer as vi
import streamlit as st
import time
import applogger


logger = applogger.get_logger(__name__)

def run_simulation(num_durchlaeufen, preis_pro_stunde, ort):
    durchlauf_ergebnisse = []
    for _ in range(num_durchlaeufen):
        jahresergebnisse = list(sim.run_experiments(preis_pro_stunde=preis_pro_stunde, ort=ort))
        durchlauf_ergebnisse.append(DurchlaufErgebnis(jahresergebnisse))
    return durchlauf_ergebnisse


def main():
    ##----------------------- Hauptprogramm: Streamlit App --------------------------------------
    # Titel
    st.set_page_config(page_title="Bike-Verleihstationen", page_icon="🚲")
    st.title("Monte Carlo Simulation")
    st.header("Bike-Verleihstationen in Dresden 🚲")
    # Eingabefelder
    preis_pro_stunde = st.number_input("Preis pro Stunde (€):", min_value=1.0, max_value=10.0, value=5.0, step=0.5)
    ort = st.selectbox("Ort:", Stationen.ALL_NAMES, index=2)
    durchlaeufe = st.number_input("Anzahl der Durchläufe:", min_value=1, max_value=40, value=10, step=1)
    # Button für die Simulation
    if st.button("Simulation starten"):
        with st.spinner("Simulation läuft..."):
            try:
                start_time = time.perf_counter()
                sim_results = run_simulation(durchlaeufe, preis_pro_stunde, ort)
                end_time = time.perf_counter()
                elapsed_time = end_time - start_time
                st.success(f"Simulation abgeschlossen in {elapsed_time:.2f} Sekunden!")
                st.balloons()

                stat_results = StatistikErgebnis(sim_results)
                vi.display_tabular(stat_results)
                vi.plot_max_profit_a_run(sim_results)
                vi.plot_profit_by_month(stat_results)
                vi.plot_profit_by_day(stat_results)

            except Exception as e:
                logger.error(f"Fehler bei der Simulation: {e}")
                st.error("Fehler bei der Simulation: " + str(e))
                
if __name__ == "__main__":
    main()

