import numpy as np
import calendar
import data 
import heapq

jahr = 2025

def run_monte_carlo(ort = data.Ortvariablen.GANZ_DRESDEN.name, preis_pro_stunde = 5, experiments = 1000):
    """
    :rtype: list[Jahresergebnis]
    """
    jahresergebnisse = []

    for _ in range(experiments):
        jahresergebnis = Jahresergebnis()
        for monat in range(12):
            monatsergebnis = Monatsergebnis(jahr, monat)
            anzahl_tage = monatsergebnis.anzahl_tage
            for tag in range(anzahl_tage):
                tagesergebnis = Tagesergebnis(monat, ort, preis_pro_stunde)
                monatsergebnis.add_tagesergebnis(tagesergebnis)
            jahresergebnis.add_monatsergebnis(monatsergebnis)  
        jahresergebnisse.append(jahresergebnis)
    return jahresergebnisse

            
class Jahresergebnis:
    def __init__(self):
        self._monatsergebnisse: list[Monatsergebnis] = []

    @property
    def anzahl_tage(self):
        return sum(monatsergebnis.anzahl_tage for monatsergebnis in self._monatsergebnisse)

    @property
    def treffer(self):
        return sum(monatsergebnis.treffer for monatsergebnis in self._monatsergebnisse)

    @property
    def treffer_quote(self):
        return round(100 * self.treffer / self.anzahl_tage if self._monatsergebnisse else 0, 2)
    
    def max_monatsergebnis(self):
        return max(self._monatsergebnisse, key=lambda x: x.max_tagesergebnis().gewinn) if self._monatsergebnisse else None
        
    @property
    def gewinn(self):
        return sum(monatsergebnis.gewinn for monatsergebnis in self._monatsergebnisse)

    def add_monatsergebnis(self, monatsergebnis):
        self._monatsergebnisse.append(monatsergebnis)

    @property
    def monatsergebnisse(self):
        """
        :rtype: list[Monatsergebnis]
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
    def __init__(self, jahr, monat):
        self.monat = monat
        self.anzahl_tage = calendar.monthrange(jahr, monat + 1)[1]
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
    LAMBDA_BASIS = 0.002
    VARKOSTEN_PRO_STUNDE = 0.5

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
        self.kundenzahl = np.random.poisson(self.erwartete_kundenzahl)
        self.mietdauer = np.random.randint(1, 6, size=self.kundenzahl)
        self.umsatz = np.sum(preis_pro_stunde * self.mietdauer)
        self.varkosten = np.sum(self.VARKOSTEN_PRO_STUNDE * self.mietdauer)
        self.gewinn = round(self.umsatz - self.varkosten - self.ort.fixkosten_pro_tag, 2)
    
    def ist_treffer(self):
        return self.gewinn > 0 # oder andere erwarteter Gewinn

    @property
    def erwartete_kundenzahl(self):
        return self.bevoelkerungszahl * self.saisonfaktor * self.LAMBDA_BASIS * self.temperaturfaktor * self.konkurrenzfaktor

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
    
    def mietdauerbereich(self):
        if self.temperatur < 10:
            return 0.5, 1.5
        elif 10 <= self.temperatur < 15:
            return 1.5, 2.5

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
    