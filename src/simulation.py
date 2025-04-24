import numpy as np


def run_monte_carlo(ort = "Gesamt", preis_pro_stunde = 3, experiments = 10000):
    jahresergebnis  = Jahresergebnis()
    wochentagen = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

    for monat in range(12):
        monatsergebnis = Monatsergebnis(monat)
        hit = 0
        for _ in range(experiments):
            tagesergebnis = Tagesergebnis(monat, ort, preis_pro_stunde)

            if tagesergebnis.gewinn > 0:
                hit += 1
            
            monatsergebnis.max_tagesergebnis = tagesergebnis

        monatsergebnis.hit_rate = hit / experiments
        jahresergebnis.add_monatsergebnis(monatsergebnis)
    return jahresergebnis
        
            
class Jahresergebnis:
    """
    Diese Klasse speichert die Ergebnisse der Monte Carlo Simulation für ein Jahr.
    """
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
        Gibt die Ergebnisse für jeden Monat zurück.
        :rtype: list[Monatsergebnis]
        """
        return self._monatsergebnisse
    
    def monatsergebnis(self, monat):
        """
        Gibt die Ergebnisse für einen bestimmten Monat zurück.
        :param monat: Der Monat (0-11)
        :return: Das Ergebnis für den angegebenen Monat
        """
        if monat < 0 or monat > 11:
            raise ValueError("Monat muss zwischen 0 und 11 liegen.")
        return self._monatsergebnisse[monat]
    
    def monatsgewinn(self, monat):
        """
        Gibt den Gewinn für einen bestimmten Monat zurück.
        :param monat: Der Monat (0-11)
        :return: Der Gewinn für den angegebenen Monat
        """
        if monat < 0 or monat > 11:
            raise ValueError("Monat muss zwischen 0 und 11 liegen.")
        return self._monatsergebnisse[monat].max_gewinn
    
    def monat_hit_rate(self, monat):
        """
        Gibt die Hit-Rate für einen bestimmten Monat zurück.
        :param monat: Der Monat (0-11)
        :return: Die Hit-Rate für den angegebenen Monat
        """
        if monat < 0 or monat > 11:
            raise ValueError("Monat muss zwischen 0 und 11 liegen.")
        return self._monatsergebnisse[monat].hit_rate
    
    def to_dict(self):
        data = []
        for monatsergebnis in self._monatsergebnisse:
            data.append(monatsergebnis.to_dict())
        return data

    
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
    def __init__(self, monat):
        self.monat = monat
        self._max_tagesergebnis = None
        self.hit_rate = 0

    @property
    def max_tagesergebnis(self):
        return self._max_tagesergebnis
    
    @max_tagesergebnis.setter
    def max_tagesergebnis(self, tagesergebnis):
        if self._max_tagesergebnis is None:
            self._max_tagesergebnis = tagesergebnis
        else:
            if self._max_tagesergebnis.gewinn < tagesergebnis.gewinn:
                self._max_tagesergebnis = tagesergebnis

    @property
    def max_gewinn(self):
        return self._max_tagesergebnis.gewinn if self._max_tagesergebnis else 0

    def to_dict(self):
        return {
            "Monat": self.monat + 1,
            "Gewinn": f"{self.max_gewinn} €",
            "Hit": f"{self.hit_rate * 100:.2f} %"
        }
    
    def to_tuple(self):
        return [self.monat + 1, f"{self.max_gewinn} €", f"{self.hit_rate * 100:.2f} %"]

    def __str__(self):
        return f"Monat: {self.monat + 1}, Gewinn: {self.max_gewinn:.2f}, Hit: {self.hit_rate * 100:.2f} %"


class Tagesergebnis:
    def __init__(self, monat, ort, preis_pro_stunde):
        self.monat = monat
        self.ort = ort
        self.lamda_basis = 0.002
        self.varkosten_pro_stunde = 0.5
        self.fixkosten_pro_tag = Datenquelle.fixkosten_pro_tag(ort)
        self.temperatur = np.random.normal(self.mw_temperatur, 5)
        self.bevoelkerung = np.random.normal(self.mw_bevoelkerung, 1000)
        self.konkurenzindex = np.random.uniform(0, 1)
        self.kundenzahl = np.random.poisson(self.erwartete_kundenzahl)
        self.mietdauer = np.random.randint(1, 6, size=self.kundenzahl)
        self.umsatz = np.sum(preis_pro_stunde * self.mietdauer)
        self.varkosten = np.sum(self.varkosten_pro_stunde * self.mietdauer)
        self.gewinn = round(self.umsatz - self.varkosten - self.fixkosten_pro_tag, 2)

    @property
    def erwartete_kundenzahl(self):
        return self.bevoelkerung * self.saisonfaktor * self.lamda_basis * self.temperaturfaktor * self.konkurrenzfaktor

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
        return 1 + (self.uebernachtungen / (self.aufenthaltsdauer * self.bevoelkerung))
    
    def mietdauerbereich(self):
        if self.temperatur < 10:
            return 0.5, 1.5
        elif 10 <= self.temperatur < 15:
            return 1.5, 2.5

    @property
    def mw_temperatur(self):
        return Datenquelle.mw_temperatur(self.monat)

    @property
    def mw_bevoelkerung(self):
        return Datenquelle.mw_bevoelkerung(self.ort)

    @property
    def uebernachtungen(self):
        return Datenquelle.uebernachtungen(self.monat)

    @property
    def aufenthaltsdauer(self):
        return Datenquelle.aufenthaltsdauer(self.monat)

    @property
    def stadtbevoelkerung(self):
        return Datenquelle.stadtbevoelkerungszahl
    
    def __str__(self):
        return f"Monat: {self.monat + 1}, Ort: {self.ort}, Temperatur: {self.temperatur:.2f}"

    def __repr__(self):
        return str(self)


class Datenquelle:
    mw_temperatur_monate = [2, 4, 8, 12, 16, 20, 24, 22, 18, 14, 8, 4]
    mw_bevoelkerung_orte = {
        "Altstadt": 2707,
        "Neustadt": 7974,
        "Südvorstadt": 23345
    }
    fixkosten_pro_tag_orte = { 
        "Altstadt": 300,
        "Neustadt": 400,
        "Südvorstadt": 600
    }
    uebernachtungen_monate = [202020, 212069, 315471, 390638, 422176, 402027, 411270, 447823, 439726, 430568, 304066, 459610]
    aufenthaltsdauer_monate = [2.05, 2.07, 2.14, 2.23, 2.16, 2.12, 2.03, 2.08, 2.08, 2.25, 1.97, 2.14]
    stadtbevoelkerungszahl = 572240
    
    @staticmethod
    def mw_temperatur(monat):
        return Datenquelle.mw_temperatur_monate[monat]  
    
    @staticmethod
    def uebernachtungen(monat):
        return Datenquelle.uebernachtungen_monate[monat]
    
    @staticmethod
    def aufenthaltsdauer(monat):
        return Datenquelle.aufenthaltsdauer_monate[monat]

    @staticmethod
    def mw_bevoelkerung(ort):
        if ort == "Gesamt":
            return np.sum(list(Datenquelle.mw_bevoelkerung_orte.values()))
        if ort not in Datenquelle.mw_bevoelkerung_orte:
            raise ValueError(f"Ort {ort} nicht gefunden.")
        return Datenquelle.mw_bevoelkerung_orte[ort]
    
    @staticmethod
    def fixkosten_pro_tag(ort):
        if ort == "Gesamt":
            return np.sum(list(Datenquelle.fixkosten_pro_tag_orte.values()))
        if ort not in Datenquelle.fixkosten_pro_tag_orte:
            raise ValueError(f"Ort {ort} nicht gefunden.")
        return Datenquelle.fixkosten_pro_tag_orte[ort]