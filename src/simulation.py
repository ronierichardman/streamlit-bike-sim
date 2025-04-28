from concurrent.futures import ProcessPoolExecutor
import numpy as np
import calendar
from data import Ortvariablen, Ortvariable, Monatsvariablen, Monatsvariable, \
    Wetterlagen, Wochentage, LAMBDA_BASIS, VARKOSTEN_PRO_STUNDE
from functools import cached_property
import os
import applogger

logger = applogger.get_logger(__name__)

jahr = 2025
anzahl_tage_monate = [calendar.monthrange(jahr, monat + 1)[1] for monat in range(12)]
anzahl_tage_jahr = sum(anzahl_tage_monate)

def run_monte_carlo_original(ort = Ortvariablen.GANZ_DRESDEN.name, preis_pro_stunde = 5, experiments = 1000):
    jahresergebnisse = []
    for _ in range(experiments):
        jahresergebnis = Jahresergebnis(anzahl_tage_jahr)
        monat_data = [Monatsvariablen.get(m) for m in range(12)]
        ort_data = Ortvariablen.get(ort)

        for monat in range(12):
            anzahl_tage = anzahl_tage_monate[monat]
            monatsergebnis = Monatsergebnis(monat=monat, anzahl_tage=anzahl_tage)
            for tag in range(anzahl_tage):
                tagesergebnis = Tagesergebnis(monat_data=monat_data[monat], ort_data=ort_data, preis_pro_stunde=preis_pro_stunde)
                monatsergebnis.add_tagesergebnis(tagesergebnis)
            jahresergebnis.add_monatsergebnis(monatsergebnis)  
        jahresergebnisse.append(jahresergebnis)
    return jahresergebnisse


def run_monte_carlo(ort = Ortvariablen.GANZ_DRESDEN.name, preis_pro_stunde = 5, experiments = 1000):
    """
    :rtype: list[Jahresergebnis]
    """
    logger.info(f"Starte Monte Carlo Simulation für {ort} mit {experiments} Experimenten.")
    ort_data = Ortvariablen.get(ort)
    logger.info(f"Ort: {ort_data.name}, Einwohner: {ort_data.einwohner}, Fixkosten pro Tag: {ort_data.fixkosten_pro_tag} €")
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        jahresergebnisse = list(executor.map(
            run_single_experiment,
            [ort_data] * experiments,
            [preis_pro_stunde] * experiments
        ))
    logger.info(f"Monte Carlo Simulation abgeschlossen. {len(jahresergebnisse)} Ergebnisse generiert.")
    return jahresergebnisse

def run_single_experiment(ort_data, preis_pro_stunde):
    jahresergebnis = Jahresergebnis(anzahl_tage_jahr)
    monate_data = Monatsvariablen.ALL

    for monat in range(12):
        anzahl_tage = anzahl_tage_monate[monat]
        monatsergebnis = Monatsergebnis(monat, anzahl_tage)
        tagesergebnisse = [
            Tagesergebnis(monate_data[monat], ort_data, preis_pro_stunde) for _ in range(anzahl_tage)
        ]
        monatsergebnis.add_tagesergebnisse(tagesergebnisse)
        logger.info(f"Monat {monat}: {monatsergebnis.gewinn}")
        jahresergebnis.add_monatsergebnis(monatsergebnis)
    return jahresergebnis
            
class Jahresergebnis:
    def __init__(self, anzahl_tage):
        self._monatsergebnisse: list[Monatsergebnis] = []
        self.anzahl_tage = anzahl_tage

    @cached_property
    def treffer(self):
        return np.sum([monatsergebnis.treffer for monatsergebnis in self._monatsergebnisse])

    @cached_property
    def trefferquote(self):
        return round(100 * self.treffer / self.anzahl_tage if self._monatsergebnisse else 0, 2)
    
    @cached_property
    def max_monatsergebnis(self):
        return np.max(self._monatsergebnisse, key=lambda x: x.max_tagesergebnis().gewinn) if self._monatsergebnisse else None
        
    @cached_property
    def gewinn(self):
        return round(np.sum([monatsergebnis.gewinn for monatsergebnis in self._monatsergebnisse]), 2)

    def add_monatsergebnis(self, monatsergebnis):
        self._monatsergebnisse.append(monatsergebnis)

    @property
    def monatsergebnisse(self):
        """
        :rtype: [Monatsergebnis]
        """
        return self._monatsergebnisse
    
    def monatsergebnis(self, monat):
        """
        :rtype: Monatsergebnis
        """
        if monat < 0 or monat > 11:
            raise ValueError("Monat muss zwischen 0 und 11 liegen.")
        return self._monatsergebnisse[monat]
    
    def to_list(self):
        return [ f"{self.gewinn} €", f"{self.trefferquote} %" ]
    
    def __str__(self):
        ergebnisse = []
        for monatsergebnis in self._monatsergebnisse:
            ergebnisse.append(str(monatsergebnis))
        result = "\n".join(ergebnisse)
        result += f"\nJahresgewinn: {self.gewinn:.2f}"
        return result
    
    def __repr__(self):
        return f"{self.__class__.__name__}(Monate={self._monatsergebnisse})"

    
class Monatsergebnis:
    def __init__(self, monat, anzahl_tage):
        self.monat = monat
        self.anzahl_tage = anzahl_tage
        self._tagesergebnisse: list[Tagesergebnis] = []

    @cached_property
    def treffer(self):
        return sum(t.ist_treffer() for t in self._tagesergebnisse)

    @cached_property
    def trefferquote(self):
        return round(100 * self.treffer / self.anzahl_tage if self.anzahl_tage > 0 else 0, 2)
    
    def add_tagesergebnis(self, tagesergebnis):
        self._tagesergebnisse.append(tagesergebnis)

    def add_tagesergebnisse(self, tagesergebnisse):
        self._tagesergebnisse = tagesergebnisse

    @cached_property
    def max_tagesergebnis(self):
        return max(self._tagesergebnisse, key=lambda x: x.gewinn) if self._tagesergebnisse else None
    
    @cached_property
    def min_tagesergebnis(self):
        return min(self._tagesergebnisse, key=lambda x: x.gewinn) if self._tagesergebnisse else None
    
    @cached_property
    def gewinn(self):
        return round(np.sum([tagesergebnis.gewinn for tagesergebnis in self._tagesergebnisse]), 2)
    
    def to_list(self):
        return [ self.monat + 1, f"{self.gewinn} €", f"{self.trefferquote} %" ]

    def __str__(self):
        return f"Monat: {self.monat + 1}, Gewinn: {self.gewinn:.2f}, Treffer: {self.trefferquote} %"

class Tagesergebnis:

    def __init__(self, monat_data: Monatsvariable, 
                 ort_data: Ortvariable, 
                 preis_pro_stunde: float):
        
        self.ort = ort_data
        self.monat_data = monat_data
        self.temperatur = np.random.normal(self.monat_data.temperatur, self.monat_data.temp_abweichung)
        self.bevoelkerungszahl = np.random.normal(self.ort.einwohner, self.monat_data.einwohner_abweichung_rate * self.ort.einwohner)
        self.konkurenzindex = np.random.uniform(0, 1)
        self.wetter = np.random.choice(Wetterlagen.ALL, p=[0.6, 0.3, 0.1])
        self.wochentag = np.random.choice(Wochentage.ALL)
        self.kundenzahl = np.random.poisson(self.erwartete_kundenzahl)
        self.mietdauer = np.random.randint(self.mietdauerbereich[0], self.mietdauerbereich[1]+1, size=self.kundenzahl)
        self.umsatz = np.sum(preis_pro_stunde * self.mietdauer)
        self.varkosten = np.sum(VARKOSTEN_PRO_STUNDE * self.mietdauer)
        self.gewinn = round(self.umsatz - self.varkosten - self.ort.fixkosten_pro_tag, 2)
    
    def ist_treffer(self):
        return self.gewinn > 0 # oder andere erwarteter Gewinn

    @cached_property
    def erwartete_kundenzahl(self):
        # logger.debug(f"{self.touristfaktor}, {self.bevoelkerungszahl}, {self.temperaturfaktor}, {self.konkurrenzfaktor}, {self.wetterfaktor}, {self.wochentagfaktor}")
        result = self.bevoelkerungszahl * self.touristfaktor * LAMBDA_BASIS \
                * self.temperaturfaktor \
                * self.wetterfaktor * self.wochentagfaktor
        logger.debug(f"Erwartete Kundenzahl: {result}")
        if result is None or result <= 0 or np.isnan(result):
            # logger.debug(f"Ungültige erwartete Kundenzahl: {result}")
            result = 0
        return result

    @cached_property
    def wochentagfaktor(self):
        if self.wochentag in Wochentage.WOCHENENDE:
            return 1.5
        else:
            return 1.0

    @cached_property
    def wetterfaktor(self):
        if self.wetter == Wetterlagen.SONNIG:
            return 1.5
        elif self.wetter == Wetterlagen.BEWOELKT:
            return 1.0
        else:
            return 0.5

    @cached_property
    def konkurrenzfaktor(self):
        return 1 - 0.7 * self.konkurenzindex

    @cached_property
    def temperaturfaktor(self):
        if self.temperatur < 10:
            return 0.3
        elif 10 <= self.temperatur < 15:
            return 0.6
        elif 15 <= self.temperatur < 22:
            return 0.9
        elif 22 <= self.temperatur < 30:
            return 1.5
        else:
            return 1.0      
    
    @cached_property
    def touristfaktor(self):
        return self.monat_data.tourist.faktor
        # return 1 + (self.uebernachtungen / (self.aufenthaltsdauer * self.bevoelkerungszahl))
    
    @cached_property
    def mietdauerbereich(self):
        """
        :rtype: tuple[int, int]
        """
        (a, b) = (1, 2)
        if self.wetter != Wetterlagen.REGEN:
            if self.temperatur < 20:
                if self.wochentag in Wochentage.WOCHENENDE:
                    (a, b) = (1, 3)
            elif self.temperatur < 28:
                if self.wochentag in Wochentage.WOCHENENDE:
                    (a, b) = (2, 5)
                else:
                    (a, b) = (1, 4)
            else:
                if self.wochentag in Wochentage.WOCHENENDE:
                    (a, b) = (2, 4)
                else:
                    (a, b) = (1, 3)
        return (a, b)
    
    @cached_property
    def uebernachtungen(self):
        return self.monat_data.tourist.uebernachtungen

    @cached_property
    def aufenthaltsdauer(self):
        return self.monat_data.tourist.aufenthaltsdauer


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