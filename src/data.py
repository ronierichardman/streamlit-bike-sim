from dataclasses import dataclass

# Wie hoch ist die Wahrscheinlichkeit, dass ein einzelner Einwohner an einem Tag ein Fahrrad mietet?
# Quelle: Mobility Behavior of Urban Populations: A Review
# Reports bike use rates of ~0.1–0.3% per person per day in European cities.
LAMBDA_BASIS = 0.003
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
    monat_name: str
    temperatur: float
    temp_abweichung: float
    einwohner_abweichung_rate: float
    tourist: Tourist

@dataclass
class Station:
    name: str
    einwohner: int
    fixkosten_pro_tag: float
    miete_pro_tag: int
    lambda_basis: float = None

    def __post_init__(self):
        self.lambda_basis = max(self.miete_pro_tag / self.einwohner, LAMBDA_BASIS)

class Wetterlagen:
    SONNIG = Wetterlage(name="Sonnig")
    BEWOELKT = Wetterlage(name="Bewölkt")
    REGEN = Wetterlage(name="Regen")
    ALL = [SONNIG, BEWOELKT, REGEN]
    ALL_NAMES = [SONNIG.name, BEWOELKT.name, REGEN.name]

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
    JANUAR = Monatsvariable(monat=0, temperatur=2, temp_abweichung=5, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=202020, aufenthaltsdauer=2.05), monat_name="Jan")
    FEBRUAR = Monatsvariable(monat=1, temperatur=4, temp_abweichung=5, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=212069, aufenthaltsdauer=2.07), monat_name="Feb")
    MAERZ = Monatsvariable(monat=2, temperatur=8, temp_abweichung=5, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=315471, aufenthaltsdauer=2.14), monat_name="Mrz")
    APRIL = Monatsvariable(monat=3, temperatur=12, temp_abweichung=10, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=390638, aufenthaltsdauer=2.23), monat_name="Apr")
    MAI = Monatsvariable(monat=4, temperatur=16, temp_abweichung=10, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=422176, aufenthaltsdauer=2.16), monat_name="Mai")
    JUNI = Monatsvariable(monat=5, temperatur=20, temp_abweichung=10, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=402027, aufenthaltsdauer=2.12), monat_name="Jun")
    JULI = Monatsvariable(monat=6, temperatur=24, temp_abweichung=10, einwohner_abweichung_rate=0.1, tourist=Tourist(uebernachtungen=411270, aufenthaltsdauer=2.03), monat_name="Jul")
    AUGUST = Monatsvariable(monat=7, temperatur=22, temp_abweichung=10, einwohner_abweichung_rate=0.1, tourist=Tourist(uebernachtungen=447823, aufenthaltsdauer=2.08), monat_name="Aug")
    SEPTEMBER = Monatsvariable(monat=8, temperatur=18, temp_abweichung=10, einwohner_abweichung_rate=0.1, tourist=Tourist(uebernachtungen=439726, aufenthaltsdauer=2.08), monat_name="Sep")
    OKTOBER = Monatsvariable(monat=9, temperatur=14, temp_abweichung=5, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=430568, aufenthaltsdauer=2.25), monat_name="Okt")
    NOVEMBER = Monatsvariable(monat=10, temperatur=8, temp_abweichung=5, einwohner_abweichung_rate=0.05, tourist=Tourist(uebernachtungen=304066, aufenthaltsdauer=1.97), monat_name="Nov")
    DEZEMBER = Monatsvariable(monat=11, temperatur=4, temp_abweichung=5, einwohner_abweichung_rate=0.1, tourist=Tourist(uebernachtungen=459610, aufenthaltsdauer=2.14), monat_name="Dez")
    ALL = [
        JANUAR, FEBRUAR, MAERZ, APRIL, MAI, JUNI,
        JULI, AUGUST, SEPTEMBER, OKTOBER, NOVEMBER, DEZEMBER
    ]
    ALL_NAMES = [
        JANUAR.monat_name, FEBRUAR.monat_name, MAERZ.monat_name, APRIL.monat_name, MAI.monat_name, JUNI.monat_name,
        JULI.monat_name, AUGUST.monat_name, SEPTEMBER.monat_name, OKTOBER.monat_name, NOVEMBER.monat_name, DEZEMBER.monat_name
    ]

    @staticmethod
    def get(monat) -> Monatsvariable:
        for monatsaenderung in Monatsvariablen.ALL:
            if monatsaenderung.monat == monat:
                return monatsaenderung
        raise ValueError(f"Monatsvariablen für Monat {monat} nicht gefunden.")

    
class Stationen:
    ALTSTADT = Station(name="Altstadt", einwohner=2707, fixkosten_pro_tag=400, miete_pro_tag=100)
    NEUSTADT = Station(name="Neustadt", einwohner=7974, fixkosten_pro_tag=400, miete_pro_tag=100)
    SUEDVORSTADT = Station(name="Südvorstadt", einwohner=23345, fixkosten_pro_tag=500, miete_pro_tag=150)
    
    ALL = [ ALTSTADT, NEUSTADT, SUEDVORSTADT ]
    ALL_NAMES = [ALTSTADT.name, NEUSTADT.name, SUEDVORSTADT.name]

    GANZ_DRESDEN = Station(
        name="Ganz Dresden", 
        einwohner=sum(f.einwohner for f in ALL), 
        fixkosten_pro_tag=sum(f.fixkosten_pro_tag for f in ALL),
        miete_pro_tag=sum(f.miete_pro_tag for f in ALL)
    )

    @staticmethod
    def get(name) -> Station:
        if name == "Ganz Dresden":
            return Stationen.GANZ_DRESDEN
        for ort_var in Stationen.ALL:
            if ort_var.name == name:
                return ort_var
        raise ValueError(f"Ort {name} nicht gefunden.")
    