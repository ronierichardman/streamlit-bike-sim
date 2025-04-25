import numpy as np
import calendar
import data 
import heapq

jahr = 2025

def run_monte_carlo(ort = data.Ortvariablen.GANZ_DRESDEN.name, preis_pro_stunde = 3, experiments = 10000):
    jahresergebnisse = []
    for _ in range(experiments):
        jahresergebnis = Jahresergebnis()
        hit = 0
        for monat in range(12):
            monatsergebnis = Monatsergebnis(jahr, monat)
            anzahl_tage = monatsergebnis.anzahl_tage
            for tag in range(anzahl_tage):
                tagesergebnis = Tagesergebnis(monat, ort, preis_pro_stunde)
                if tagesergebnis.gewinn > 0:
                    hit += 1
                monatsergebnis.add_tagesergebnis(tagesergebnis)
            monatsergebnis.hit_rate = hit / anzahl_tage
            jahresergebnis.add_monatsergebnis(monatsergebnis)  
        jahresergebnisse.append(jahresergebnis)
    return jahresergebnisse

        
            
class Jahresergebnis:
    def __init__(self):
        self._monatsergebnisse: list[Monatsergebnis] = []
        self._jahresgewinn = 0
    
    def add_monatsergebnis(self, monatsergebnis):
        self._monatsergebnisse.append(monatsergebnis)
        self._jahresgewinn += monatsergebnis.max_gewinn
    
    @property
    def jahresgewinn(self):
        return self._jahresgewinn

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
    
    def monatsgewinn(self, monat):
        if monat < 0 or monat > 11:
            raise ValueError("Monat muss zwischen 0 und 11 liegen.")
        return self._monatsergebnisse[monat].max_gewinn
    
    def monat_hit_rate(self, monat):
        if monat < 0 or monat > 11:
            raise ValueError("Monat muss zwischen 0 und 11 liegen.")
        return self._monatsergebnisse[monat].hit_rate
    
    def __str__(self):
        ergebnisse = []
        for monatsergebnis in self._monatsergebnisse:
            ergebnisse.append(str(monatsergebnis))
        result = "\n".join(ergebnisse)
        result += f"\nJahresgewinn: {self._jahresgewinn:.2f}"
        return result
    
    def __repr__(self):
        return f"{self.__class__.__name__}(Monate={self._monatsergebnisse})"

    
    
class Monatsergebnis:
    def __init__(self, jahr, monat):
        self.monat = monat
        self.anzahl_tage = calendar.monthrange(jahr, monat + 1)[1]
        self._tagesergebnisse: list[Tagesergebnis] = []
        self.hit_rate = 0

    def add_tagesergebnis(self, tagesergebnis):
        if len(self._tagesergebnisse) < self.anzahl_tage:
            heapq.heappush(self._tagesergebnisse, tagesergebnis)
        else:
            heapq.heappushpop(self._tagesergebnisse, tagesergebnis)

    def max_tagesgewinn(self):
        return heapq.nlargest(1, self._tagesergebnisse)[0].gewinn if self._tagesergebnisse else 0
    
    def sum_tagesgewinn(self):
        return sum(tagesergebnis.gewinn for tagesergebnis in self._tagesergebnisse)


    def to_dict(self):
        return {
            "Monat": self.monat + 1,
            "Gewinn": f"{self.sum_tagesgewinn()} €",
            "Hit": f"{self.hit_rate * 100:.2f} %"
        }
    
    def to_tuple(self):
        return [self.monat + 1, f"{self.sum_tagesgewinn()} €", f"{self.hit_rate * 100:.2f} %"]

    def __str__(self):
        return f"Monat: {self.monat + 1}, Gewinn: {self.sum_tagesgewinn():.2f}, Hit: {self.hit_rate * 100:.2f} %"


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

    def ist_erreichter_gewinn(self):
        return self.gewinn >= self.ort.erwarteter_gewinn_pro_tag

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
    