from concurrent.futures import ProcessPoolExecutor
from models import Jahresergebnis, Monatsergebnis, Tagesergebnis
import calendar
from data import Stationen, Monatsvariablen
import os
import applogger

logger = applogger.get_logger(__name__)

jahr = 2025
anzahl_tage_monate = [calendar.monthrange(jahr, monat + 1)[1] for monat in range(12)]
anzahl_tage_jahr = sum(anzahl_tage_monate)

def run_experiments(ort=Stationen.SUEDVORSTADT.name, preis_pro_stunde=5, experiments=1000):
    """
    :rtype: Generator[Jahresergebnis, None, None]
    """
    logger.info(f"Starte Monte Carlo Simulation für {ort} mit {experiments} Experimenten.")
    ort_data = Stationen.get(ort)
    with ProcessPoolExecutor(max_workers=min(8, os.cpu_count())) as executor:
        for result in executor.map(
            run_single_experiment,
            [ort_data] * experiments,
            [preis_pro_stunde] * experiments
        ):
            yield result

    logger.info(f"Monte Carlo Simulation abgeschlossen.")


def run_single_experiment(ort_data, preis_pro_stunde) -> Jahresergebnis:
    jahresergebnis = Jahresergebnis(anzahl_tage_jahr)
    monate_data = Monatsvariablen.ALL

    for monat in range(12):
        anzahl_tage = anzahl_tage_monate[monat]
        monatsergebnis = Monatsergebnis(monat, anzahl_tage)
        tagesergebnisse = [
            Tagesergebnis(monate_data[monat], ort_data, preis_pro_stunde) for _ in range(anzahl_tage)
        ]
        monatsergebnis.set_tagesergebnisse(tagesergebnisse)
        jahresergebnis.add_monatsergebnis(monatsergebnis)
    return jahresergebnis


# Todo: Use NumPy for vectorized computations
# def precompute_temperatur(monat_data, anzahl_tage):
#     temperatures = np.random.normal(loc=monat_data.temperatur, scale=monat_data.temp_abweichung, size=anzahl_tage)
#     temperatur_faktoren = np.where(
#         temperatures < 10, 0.3,
#         np.where(
#             temperatures < 15, 0.6,
#             np.where(
#                 temperatures < 22, 0.9,
#                 np.where(temperatures < 30, 1.2, 1.0)
#             )
#         )
#     )
#     return temperatures, temperatur_faktoren