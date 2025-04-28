from dataclasses import dataclass

LAMBDA_BASIS = 0.02
VARKOSTEN_PRO_STUNDE = 0.5
STADT_EINWOHNER = 572240

@dataclass(frozen=True)
class Wetterlage:
    name: str

@dataclass(frozen=True)
class Wochentag:
    name: str

@dataclass
class Tourist:
    uebernachtungen: int
    aufenthaltsdauer: float
    faktor: float = None

    def __post_init__(self):
        self.faktor = 1 + (self.uebernachtungen / (self.aufenthaltsdauer * STADT_EINWOHNER)) 

@dataclass(frozen=True)
class Monatsvariable:
    monat: int
    temperatur: float
    temp_abweichung: float
    einwohner_abweichung_rate: float
    tourist: Tourist

@dataclass(frozen=True)
class Ortvariable:
    name: str
    einwohner: int
    fixkosten_pro_tag: float
    erwarteter_gewinn_pro_tag: float 

@dataclass(frozen=True)
class Touristvariable:
    monat : int
    uebernachtungen: int
    aufenthaltsdauer: float
    faktor: float

class Wetterlagen:
    SONNIG = Wetterlage(name="sonnig")
    BEWOELKT = Wetterlage(name="bewölkt")
    REGEN = Wetterlage(name="regen")
    ALL = [SONNIG, BEWOELKT, REGEN]

    def __eq__(self, other):
        return self.name == other.name
        
class Wochentage:
    MO = Wochentag(name="Mo")
    DI = Wochentag(name="Di")
    MI = Wochentag(name="Mi")
    DO = Wochentag(name="Do")
    FR = Wochentag(name="Fr")
    SA = Wochentag(name="Sa")
    SO = Wochentag(name="So")
    ALL = [MO, DI, MI, DO, FR, SA, SO]
    WOCHENENDE = [SA, SA]

    def __eq__(self, other):
        return self.name == other.name

class Monatsvariablen:
    JANUAR = Monatsvariable(monat=0, temperatur=2, temp_abweichung=5, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=202020, aufenthaltsdauer=2.05))
    FEBRUAR = Monatsvariable(monat=1, temperatur=4, temp_abweichung=5, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=212069, aufenthaltsdauer=2.07))
    MAERZ = Monatsvariable(monat=2, temperatur=8, temp_abweichung=5, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=315471, aufenthaltsdauer=2.14))
    APRIL = Monatsvariable(monat=3, temperatur=12, temp_abweichung=10, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=390638, aufenthaltsdauer=2.23))
    MAI = Monatsvariable(monat=4, temperatur=16, temp_abweichung=10, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=422176, aufenthaltsdauer=2.16))
    JUNI = Monatsvariable(monat=5, temperatur=20, temp_abweichung=10, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=402027, aufenthaltsdauer=2.12))
    JULI = Monatsvariable(monat=6, temperatur=24, temp_abweichung=10, einwohner_abweichung_rate=0.1, tourist=Tourist(uebernachtungen=411270, aufenthaltsdauer=2.03))
    AUGUST = Monatsvariable(monat=7, temperatur=22, temp_abweichung=10, einwohner_abweichung_rate=0.1, tourist=Tourist(uebernachtungen=447823, aufenthaltsdauer=2.08))
    SEPTEMBER = Monatsvariable(monat=8, temperatur=18, temp_abweichung=10, einwohner_abweichung_rate=0.1, tourist=Tourist(uebernachtungen=439726, aufenthaltsdauer=2.08))
    OKTOBER = Monatsvariable(monat=9, temperatur=14, temp_abweichung=5, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=430568, aufenthaltsdauer=2.25))
    NOVEMBER = Monatsvariable(monat=10, temperatur=8, temp_abweichung=5, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=304066, aufenthaltsdauer=1.97))
    DEZEMBER = Monatsvariable(monat=11, temperatur=4, temp_abweichung=5, einwohner_abweichung_rate=0.1, tourist=Tourist(uebernachtungen=459610, aufenthaltsdauer=2.14))
    ALL = [
        JANUAR, FEBRUAR, MAERZ, APRIL, MAI, JUNI,
        JULI, AUGUST, SEPTEMBER, OKTOBER, NOVEMBER, DEZEMBER
    ]

    @staticmethod
    def get(monat):
        """
        rtype: Monatsvariable
        """
        for monatsaenderung in Monatsvariablen.ALL:
            if monatsaenderung.monat == monat:
                return monatsaenderung
        raise ValueError(f"Monatsvariablen für Monat {monat} nicht gefunden.")

    
class Ortvariablen:
    ALTSTADT = Ortvariable(name="Altstadt", einwohner=2707, fixkosten_pro_tag=500, erwarteter_gewinn_pro_tag=1000)
    NEUSTADT = Ortvariable(name="Neustadt", einwohner=7974, fixkosten_pro_tag=500, erwarteter_gewinn_pro_tag=1000)
    SUEDVORSTADT = Ortvariable(name="Südvorstadt", einwohner=23345, fixkosten_pro_tag=500, erwarteter_gewinn_pro_tag=1000)
    
    ALL = [ ALTSTADT, NEUSTADT, SUEDVORSTADT ]

    GANZ_DRESDEN = Ortvariable(
        name="Ganz Dresden", 
        einwohner=sum(f.einwohner for f in ALL), 
        fixkosten_pro_tag=sum(f.fixkosten_pro_tag for f in ALL),
        erwarteter_gewinn_pro_tag=sum(f.erwarteter_gewinn_pro_tag for f in ALL)
    )

    ALL_NAMES = [ALTSTADT.name, NEUSTADT.name, SUEDVORSTADT.name, GANZ_DRESDEN.name]

    @staticmethod
    def get(name):
        """
        rtype: Ortvariable
        """
        if name == "Ganz Dresden":
            return Ortvariablen.GANZ_DRESDEN
        for ort_var in Ortvariablen.ALL:
            if ort_var.name == name:
                return ort_var
        raise ValueError(f"Ort {name} nicht gefunden.")
