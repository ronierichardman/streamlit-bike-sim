import numpy as np
from data import Station, Monatsvariable, \
    Wetterlagen, Wochentage, VARKOSTEN_PRO_STUNDE
from functools import cached_property


class Tagesergebnis:
    def __init__(self, monat_data: Monatsvariable, 
                 ort_data: Station, 
                 preis_pro_stunde: float):
        
        self.monat = monat_data.monat
        self.temperatur = np.random.normal(monat_data.temperatur, monat_data.temp_abweichung)
        self.bevoelkerungszahl = np.random.normal(ort_data.einwohner, monat_data.einwohner_abweichung_rate * ort_data.einwohner)
        self.konkurenzindex = np.random.uniform(0, 1)
        self.wetter = np.random.choice(Wetterlagen.ALL, p=[0.6, 0.3, 0.1])
        self.wochentag = np.random.choice(Wochentage.ALL)
        self.touristfaktor = monat_data.tourist.faktor
        self.kundenzahl = np.random.poisson(self.erwartete_kundenzahl(ort_data))
        self.mietdauer = np.random.randint(self.mietdauerbereich[0], self.mietdauerbereich[1]+1, size=self.kundenzahl)
        self.umsatz = np.sum(preis_pro_stunde * self.mietdauer)
        self.varkosten = np.sum(VARKOSTEN_PRO_STUNDE * self.mietdauer)
        self.gewinn = self.umsatz - self.varkosten - ort_data.fixkosten_pro_tag
    
    def erwartete_kundenzahl(self, ort: Station):
        result = self.bevoelkerungszahl * self.touristfaktor * ort.lambda_basis \
                * self.temperaturfaktor() * self.konkurrenzfaktor() \
                * self.wetterfaktor() * self.wochentagfaktor()
        if result is None or result <= 0 or np.isnan(result):
            result = 0
        return result
    
    def ist_treffer(self):
        return self.gewinn > 0 # oder andere erwarteter Gewinn

    def wochentagfaktor(self):
        if self.wochentag in Wochentage.WOCHENENDE:
            return 1.2
        else:
            return 1.0

    def wetterfaktor(self):
        if self.wetter == Wetterlagen.SONNIG:
            return 1.2
        elif self.wetter == Wetterlagen.BEWOELKT:
            return 1.0
        else:
            return 0.5

    def konkurrenzfaktor(self):
        return 1 - 0.7 * self.konkurenzindex

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
    
    @cached_property
    def mietdauerbereich(self) -> tuple[int, int]:
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
    

class Monatsergebnis:
    def __init__(self, monat, anzahl_tage):
        self.monat = monat
        self.anzahl_tage = anzahl_tage
        self._tagesergebnisse: list[Tagesergebnis] = []

    @cached_property
    def gewinn(self):
        return np.sum([tagesergebnis.gewinn for tagesergebnis in self._tagesergebnisse])

    def treffer(self):
        return np.sum([tag.ist_treffer() for tag in self._tagesergebnisse])

    def trefferquote(self):
        return 100 * self.treffer() / self.anzahl_tage if self.anzahl_tage > 0 else 0
    
    def add_tagesergebnis(self, tagesergebnis):
        self._tagesergebnisse.append(tagesergebnis)

    def set_tagesergebnisse(self, tagesergebnisse):
        self._tagesergebnisse = tagesergebnisse
    
    def tagesergebnisse(self) -> list[Tagesergebnis]:
        return self._tagesergebnisse

    def tagesergebnis(self, index) -> Tagesergebnis:
        if index < 0 or index > self.anzahl_tage:
            raise ValueError(f"Index muss zwischen 0 und {self.anzahl_tage - 1} liegen.")
        return self._tagesergebnisse[index]

    def max_tagesergebnis(self) -> Tagesergebnis:
        return max(self._tagesergebnisse, key=lambda x: x.gewinn) if self._tagesergebnisse else None
    
    def min_tagesergebnis(self) -> Tagesergebnis:
        return min(self._tagesergebnisse, key=lambda x: x.gewinn) if self._tagesergebnisse else None

    def to_list(self):
        return [ f"{self.gewinn} €", f"{self.trefferquote()} %" ]

    def __str__(self):
        return f"Gewinn: {self.gewinn:.2f} €, Trefferquote: {self.trefferquote()} %"
    

class Jahresergebnis:
    def __init__(self, anzahl_tage):
        self.anzahl_tage = anzahl_tage
        self._monatsergebnisse: list[Monatsergebnis] = []
    
    @cached_property
    def gewinn(self):
        return np.sum([monatsergebnis.gewinn for monatsergebnis in self._monatsergebnisse])
    
    def treffer(self):
        return np.sum([monatsergebnis.treffer() for monatsergebnis in self._monatsergebnisse])
    
    def trefferquote(self):
        return 100 * self.treffer() / self.anzahl_tage if self.anzahl_tage > 0 else 0
    
    def max_monatsergebnis(self) -> Monatsergebnis:
        return max(self._monatsergebnisse, key=lambda x: x.gewinn) if self._monatsergebnisse else None
    
    def min_monatsergebnis(self) -> Monatsergebnis:
        return min(self._monatsergebnisse, key=lambda x: x.gewinn) if self._monatsergebnisse else None

    def monatsergebnisse(self) -> list[Monatsergebnis]:
        return self._monatsergebnisse
    
    def monatsergebnis(self, monat) -> Monatsergebnis:
        if monat < 0 or monat > 11:
            raise ValueError("Monat muss zwischen 0 und 11 liegen.")
        return self._monatsergebnisse[monat]
    
    def tagesergebnisse(self) -> list[Tagesergebnis]:
        return [t for m in self._monatsergebnisse for t in m.tagesergebnisse()]
    
    def max_tagesergebnis(self) -> Tagesergebnis:
        return max(self.tagesergebnisse(), key=lambda x: x.gewinn)
    
    def min_tagesergebnis(self) -> Tagesergebnis:
        return min(self.tagesergebnisse(), key=lambda x: x.gewinn)
    
    def mw_monatsgewinn(self):
        return np.mean([m.gewinn for m in self._monatsergebnisse])
    
    def mw_tagesgewinn(self):
        return np.mean([t.gewinn for t in self.tagesergebnisse()])
    
    def add_monatsergebnis(self, monatsergebnis):
        self._monatsergebnisse.append(monatsergebnis)
        
    def to_list(self):
        return [ f"{round(self.gewinn):,} €", f"{round(self.max_monatsergebnis().gewinn):,} €",f"{round(self.max_tagesergebnis().gewinn):,} €",f"{self.trefferquote():.2f} %" ]
    
    def __str__(self):
        return f"{round(self.gewinn):,} € -- {self.trefferquote():.2f} %" 
    
    def __repr__(self):
        return f"{self.__class__.__name__}(Monate={self._monatsergebnisse})"
    

class DurchlaufErgebnis:
    def __init__(self, jahresergebnisse:list[Jahresergebnis]):
        self.jahresergebnisse = jahresergebnisse
        self._sorted_jahresergebnisse = None

    def sorted_jahresergebnisse(self):
        if self._sorted_jahresergebnisse == None:
            self._sorted_jahresergebnisse = sorted(self.jahresergebnisse, key=lambda x: x.gewinn)
        return self._sorted_jahresergebnisse
    
    def max_jahresergebnis(self) -> Jahresergebnis:
        return self.sorted_jahresergebnisse()[-1] if self.sorted_jahresergebnisse else None
    
    def mw_jahresgewinn(self) -> float:
        return np.mean([j.gewinn for j in self.jahresergebnisse])
    
    def min_jahresergebnis(self) -> Jahresergebnis:
        return self.sorted_jahresergebnisse()[0] if self.sorted_jahresergebnisse else None
    
    def monatsergebnisse(self, monat) -> list[Monatsergebnis]:
        if monat == -1:
            return [ m for j in self.jahresergebnisse for m in j.monatsergebnisse()]
        return [j.monatsergebnis(monat) for j in self.jahresergebnisse]
    
    def max_monatsergebnisse(self) -> list[Monatsergebnis]:
        return [ j.max_monatsergebnis() for j in self.jahresergebnisse ]
    
    def min_monatsergebnisse(self) -> list[Monatsergebnis]:
        return [ j.min_monatsergebnis() for j in self.jahresergebnisse ]
    
    def max_monatsergebnis(self, monat=-1) -> Monatsergebnis:
        if monat == -1:
            return max(self.max_monatsergebnisse(), key=lambda m: m.gewinn)
        return max(self.monatsergebnisse(monat), key=lambda m: m.gewinn)
    
    def min_monatsergebnis(self, monat=-1) -> Monatsergebnis:
        if monat == -1:
            return min(self.min_monatsergebnisse(), key=lambda m: m.gewinn)
        return min(self.monatsergebnisse(monat), key=lambda m: m.gewinn)
    
    def mw_monatsgewinn(self, monat=-1) -> float:
        if monat == -1:
            return np.mean([j.mw_monatsgewinn() for j in self.jahresergebnisse])
        return np.mean([j.monatsergebnis(monat).gewinn for j in self.jahresergebnisse])
    
    def max_tagesergebnisse(self) -> list[Tagesergebnis]:
        return [j.max_tagesergebnis() for j in self.jahresergebnisse]
    
    def min_tagesergebnisse(self) -> list[Tagesergebnis]:
        return [j.min_tagesergebnis() for j in self.jahresergebnisse]

    def mw_treffequote(self) -> float:
        return np.mean([j.trefferquote() for j in self.jahresergebnisse])
    
    def mw_tagesgewinn(self):
        return np.mean([j.mw_tagesgewinn() for j in self.jahresergebnisse])
    
    def tagesergebnisse(self) -> list[Tagesergebnis]:
        return [t for j in self.jahresergebnisse for t in j.tagesergebnisse() ]
    
    def max_tagesergebnis(self) -> Tagesergebnis:
        return max(self.max_tagesergebnisse(), key=lambda x: x.gewinn)
    
    def min_tagesergebnis(self) -> Tagesergebnis:
        return min(self.min_tagesergebnisse(), key=lambda x: x.gewinn)
    
    # def std_jahresgewinn(self):
    #     return np.std([jahresergebnis.gewinn for jahresergebnis in self.jahresergebnisse], ddof=1) if self.jahresergebnisse else 0
    
    # def varianz_gewinne(self):
    #     return np.var([jahresergebnis.gewinn for jahresergebnis in self.jahresergebnisse], ddof=1) if self.jahresergebnisse else 0
    
    # def median_gewinne(self):
    #     return np.median([jahresergebnis.gewinn for jahresergebnis in self.jahresergebnisse]) if self.jahresergebnisse else 0


class StatistikErgebnis:
    def __init__(self, durchlauf_ergebnisse: list[DurchlaufErgebnis]):
        self.durchlauf_ergebnisse = durchlauf_ergebnisse
    
    @cached_property
    def mw_jahresgewinn(self):
        return np.mean([d.mw_jahresgewinn() for d in self.durchlauf_ergebnisse])
    
    @cached_property
    def mw_trefferquote(self):
        return np.mean([d.mw_treffequote() for d in self.durchlauf_ergebnisse])
    

    def mw_monatsgewinn(self, monat=-1):
        if monat == -1:
            return np.mean([d.mw_monatsgewinn() for d in self.durchlauf_ergebnisse])
        return np.mean([ d.mw_monatsgewinn(monat) for d in self.durchlauf_ergebnisse])

    # @cached_property
    # def mw_monatsgewinne(self, monat) -> list[float]:
    #     return [ d.mw_monatsgewinn(monat) for d in self.durchlauf_ergebnisse]

    # @cached_property
    # def max_monatsgewinne(self, monat) -> list[float]:
    #     return [ d.max_monatsergebnis(monat).gewinn for d in self.durchlauf_ergebnisse ]
    
    # @cached_property
    # def min_monatsgewinne(self, monat) -> list[float]:
    #     return [ d.min_monatsergebnis(monat).gewinn for d in self.durchlauf_ergebnisse ]
    
    def monatsergebnisse(self, monat=-1) -> list[Monatsergebnis]:
        if monat == -1:
            return [ m for d in self.durchlauf_ergebnisse for m in d.monatsergebnisse() ]
        return [ m for d in self.durchlauf_ergebnisse for m in d.monatsergebnisse(monat) ]
    
    @cached_property
    def max_monatsergebnisse(self) -> list[Monatsergebnis]:
        return [ m for d in self.durchlauf_ergebnisse for m in d.max_monatsergebnisse() ]
    
    @cached_property
    def min_monatsergebnisse(self) -> list[Monatsergebnis]:
        return [ m for d in self.durchlauf_ergebnisse for m in d.min_monatsergebnisse() ]

    def max_monatsergebnis(self, monat=-1) -> Monatsergebnis:
        if monat == -1:
            return max(self.max_monatsergebnisse, key=lambda x: x.gewinn)
        return max(self.monatsergebnisse(monat), key=lambda x: x.gewinn)
    
    def min_monatsergebnis(self, monat=-1) -> Monatsergebnis:
        if monat == -1:
            return min(self.min_monatsergebnisse, key=lambda x: x.gewinn)
        return min(self.monatsergebnisse(monat), key=lambda x: x.gewinn)
    
    @cached_property
    def mw_tagesgewinn(self):
        return np.mean([d.mw_tagesgewinn() for d in self.durchlauf_ergebnisse])

    @cached_property
    def tagesergebnisse(self) -> list[Tagesergebnis]:
        return [t for d in self.durchlauf_ergebnisse for t in d.tagesergebnisse()]
    
    @cached_property
    def max_tagesergebnisse(self) -> list[Tagesergebnis]:
        return [ t for d in self.durchlauf_ergebnisse for t in d.max_tagesergebnisse()]
    
    @cached_property
    def min_tagesergebnisse(self) -> list[Tagesergebnis]:
        return [ d.min_tagesergebnis() for d in self.durchlauf_ergebnisse ]

    @cached_property
    def max_tagesergebnis(self):
        return max(self.max_tagesergebnisse, key=lambda x: x.gewinn)
    
    @cached_property
    def min_tagesergebnis(self):
        return min(self.min_tagesergebnisse, key=lambda x: x.gewinn)
    

    
