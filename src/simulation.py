from concurrent.futures import ProcessPoolExecutor
import numpy as np
import calendar
import data 
from functools import cached_property

jahr = 2025

def run_monte_carlo(ort = data.Ortvariablen.GANZ_DRESDEN.name, preis_pro_stunde = 5, experiments = 1000):
    """
    :rtype: list[Jahresergebnis]
    """
    with ProcessPoolExecutor() as executor:
        jahresergebnisse = list(executor.map(
            run_single_experiment,
            [jahr] * experiments,
            [ort] * experiments,
            [preis_pro_stunde] * experiments
        ))
    return jahresergebnisse

def run_single_experiment(jahr, ort, preis_pro_stunde):
    jahresergebnis = Jahresergebnis()
    for monat in range(12):
        anzahl_tage = calendar.monthrange(jahr, monat + 1)[1]
        monatsergebnis = Monatsergebnis(monat, anzahl_tage)
        tagesergebnisse = [
            Tagesergebnis(monat, ort, preis_pro_stunde) for _ in range(anzahl_tage)
        ]
        for tagesergebnis in tagesergebnisse:
            monatsergebnis.add_tagesergebnis(tagesergebnis)
        jahresergebnis.add_monatsergebnis(monatsergebnis)
    return jahresergebnis
            
class Jahresergebnis:
    def __init__(self, jahr):
        self._monatsergebnisse: list[Monatsergebnis] = []
        self.anzahl_tage = 366 if calendar.isleap(jahr) else 365 

    @cached_property
    def treffer(self):
        return np.sum([monatsergebnis.treffer for monatsergebnis in self._monatsergebnisse])

    @cached_property
    def treffer_quote(self):
        return round(100 * self.treffer / self.anzahl_tage if self._monatsergebnisse else 0, 2)
    
    @cached_property
    def max_monatsergebnis(self):
        return np.max(self._monatsergebnisse, key=lambda x: x.max_tagesergebnis().gewinn) if self._monatsergebnisse else None
        # return max(self._monatsergebnisse, key=lambda x: x.max_tagesergebnis().gewinn) if self._monatsergebnisse else None
        
    @cached_property
    def gewinn(self):
        return np.sum([monatsergebnis.gewinn for monatsergebnis in self._monatsergebnisse])
        # return sum(monatsergebnis.gewinn for monatsergebnis in self._monatsergebnisse)

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
        return [ f"{self.gewinn} €", f"{self.treffer_quote} %" ]
    
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

    @property
    def treffer(self):
        return sum(t.ist_treffer() for t in self._tagesergebnisse)

    @property
    def treffer_quote(self):
        return round(100 * self.treffer / self.anzahl_tage if self.anzahl_tage > 0 else 0, 2)

    def add_tagesergebnis(self, tagesergebnis):
        self._tagesergebnisse.append(tagesergebnis)

    def max_tagesergebnis(self):
        return max(self._tagesergebnisse, key=lambda x: x.gewinn) if self._tagesergebnisse else None
    
    def min_tagesergebnis(self):
        return min(self._tagesergebnisse, key=lambda x: x.gewinn) if self._tagesergebnisse else None
    
    @property
    def gewinn(self):
        return sum(tagesergebnis.gewinn for tagesergebnis in self._tagesergebnisse)
    
    def to_list(self):
        return [ self.monat + 1, f"{self.gewinn} €", f"{self.treffer_quote} %" ]

    def __str__(self):
        return f"Monat: {self.monat + 1}, Gewinn: {self.gewinn:.2f}, Treffer: {self.treffer_quote} %"


class Tagesergebnis:

    def __init__(self, monat, ort, preis_pro_stunde):
        """
        :param monat: Monat (0-11)
        :param ort: String
        :param preis_pro_stunde: Preis pro Stunde
        """
        self.monat = monat
        self.ort = data.Ortvariablen.get_filial_by_name(ort)
        self.monatsvariable = data.Monatsvariablen.get_monatsaenderung_by_monat(monat)
        self.temperatur = np.random.normal(self.monatsvariable.temperatur, self.monatsvariable.temp_abweichung)
        self.bevoelkerungszahl = np.random.normal(self.ort.einwohner, self.monatsvariable.einwohner_abweichung)
        self.konkurenzindex = np.random.uniform(0, 1)
        self.wetter = np.random.choice(data.WETTERLAGEN, p=[0.6, 0.3, 0.1])
        self.wochentag = np.random.choice(data.WOCHEN_TAGE)
        self.kundenzahl = np.random.poisson(self.erwartete_kundenzahl)
        a, b = self.mietdauerbereich
        self.mietdauer = np.random.randint(a, b+1, size=self.kundenzahl)
        self.umsatz = np.sum(preis_pro_stunde * self.mietdauer)
        self.varkosten = np.sum(data.VARKOSTEN_PRO_STUNDE * self.mietdauer)
        self.gewinn = round(self.umsatz - self.varkosten - self.ort.fixkosten_pro_tag, 2)
    
    def ist_treffer(self):
        return self.gewinn > 0 # oder andere erwarteter Gewinn

    @property
    def erwartete_kundenzahl(self):
        return self.bevoelkerungszahl * self.saisonfaktor * data.LAMBDA_BASIS * self.temperaturfaktor * self.konkurrenzfaktor * self.wetterfaktor * self.wochentagfaktor

    @property
    def wochentagfaktor(self):
        if self.wochentag in ["Sa", "So"]:
            return 1.5
        else:
            return 1.0

    @property
    def wetterfaktor(self):
        if self.wetter == "sonnig":
            return 1.2
        elif self.wetter == "bewölkt":
            return 1.0
        else:
            return 0.5

    @property
    def konkurrenzfaktor(self):
        return 1 - 0.7 * self.konkurenzindex

    @property
    def temperaturfaktor(self):
        if self.temperatur < 10:
            return 0.3
        elif 10 <= self.temperatur < 15:
            return 0.6
        elif 15 <= self.temperatur < 22:
            return 0.9
        elif 22 <= self.temperatur < 30:
            return 1.2
        else:
            return 1.0      
    
    @property
    def saisonfaktor(self):
        return 1 + (self.uebernachtungen / (self.aufenthaltsdauer * self.bevoelkerungszahl))
    
    @property
    def mietdauerbereich(self):
        """
        :rtype: tuple[int, int]
        """
        (a, b) = (1, 2)
        if self.wetter != "regen":
            if self.temperatur < 20:
                if self.wochentag in ["Sa", "So"]:
                    (a, b) = (1, 3)
            elif self.temperatur < 28:
                if self.wochentag in ["Sa", "So"]:
                    (a, b) = (2, 5)
                else:
                    (a, b) = (1, 4)
            else:
                if self.wochentag in ["Sa", "So"]:
                    (a, b) = (2, 4)
                else:
                    (a, b) = (1, 3)
        return (a, b)
    
    @property
    def uebernachtungen(self):
        return self.monatsvariable.tourist.uebernachtungen

    @property
    def aufenthaltsdauer(self):
        return self.monatsvariable.tourist.aufenthaltsdauer


    def __str__(self):
        return f"Monat: {self.monat + 1}, Ort: {self.ort.name}, Temperatur: {self.temperatur:.2f}"

    def __repr__(self):
        return str(self)
    