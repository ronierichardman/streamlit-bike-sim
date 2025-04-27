from scipy.stats import t
import numpy as np
from scipy.stats import norm
import streamlit as st
from simulation import Jahresergebnis, Monatsergebnis, Tagesergebnis
from streamlit_echarts import st_echarts


class StatisticErgebnis:
    def __init__(self, jahresgewinn,  jahresgewinn_std,
                 jahresgewinn_varianz, jahresgewinn_median, jahresgewinn_oberes_quartil, jahresgewinn_unteres_quartil,
                 jahresgewinn_t_verteilung_gamma_fraktil, jahresdewinn_ki_high, jahresdewinn_ki_low):
        self.jahresgewinn = jahresgewinn
        self.jahresgewinn_std = jahresgewinn_std
        self.jahresgewinn_varianz = jahresgewinn_varianz
        self.jahresgewinn_median = jahresgewinn_median
        self.jahresgewinn_oberes_quartil = jahresgewinn_oberes_quartil
        self.jahresgewinn_unteres_quartil = jahresgewinn_unteres_quartil
        self.jahresgewinn_t_verteilung_gamma_fraktil = jahresgewinn_t_verteilung_gamma_fraktil
        self.jahresdewinn_ki_high=jahresdewinn_ki_high
        self.jahresdewinn_ki_low=jahresdewinn_ki_low

def rechnen_durchlaeufe(durchlaeufe):
    """
    :param durchlaeufe: list[list[Jahresergebnis]]
    :param durchlaeufe: list[DurchlaufErgebnis]
    M: len(durchlaeufe) = 10 -> M < 40
    n: len(list[Jahresergebnis]) = 1000
    """
    mittelwerte = []
    for durchlauf in durchlaeufe:
        # mittelwerte.append(mittelwert(durchlauf))
        mittelwerte.append(durchlauf.durchschnitt_gewinne())
    
    mw = np.mean(mittelwerte)
    std = np.std(mittelwerte, ddof=1)  # ddof=1 für Stichprobenstandardabweichung
    varianz = np.var(mittelwerte, ddof=1)  # ddof=1 für Stichprobenvarianz
    median = np.median(mittelwerte)
    oberes_quartil = np.percentile(mittelwerte, 75)
    unteres_quartil = np.percentile(mittelwerte, 25)
    # Konfidenzniveau 90% -> 95%-Quantil der t-Verteilung mit nu Freiheitsgraden
    gamma = 0.95  # 95%-Quantil
    t_verteilung_gamma_fraktil = norm.ppf(gamma)
    ki_high=mw+t_verteilung_gamma_fraktil*(std/np.sqrt(len(mittelwerte)))
    ki_low=mw-t_verteilung_gamma_fraktil*(std/np.sqrt(len(mittelwerte)))
    result=StatisticErgebnis(mw, std, varianz, median, oberes_quartil, unteres_quartil, t_verteilung_gamma_fraktil,ki_high, ki_low)
    return result


def mittelwert(jahresergebnisse):
    """
    :param jahresergebnisse: list[Jahresergebnis]
    :return: list[float]
    """
    gewinne = []
    for jahresergebnis in jahresergebnisse:
        gewinne.append(jahresergebnis.gewinn)

    return sum(gewinne) / len(gewinne)  
  
def plot_diagram_durchlaeufe(durchlauf_ergebnisse):
    """
    :param durchlauf_ergebnisse: list[DurchlaufErgebnis]
    """
    x = []
    y = []

    for idx, durchlauf_ergebnis in enumerate(durchlauf_ergebnisse):
        x.append(idx + 1)
        y.append(durchlauf_ergebnis.durchschnitt_gewinne())

    options = {
    "xAxis": {"type": "category", "data": x},
    "yAxis": {"type": "value"},
    "series": [{"data": y,  "type": "line"}],
    }
    st_echarts(options=options, height="400px")

def plot_diagram_max_gewinn_im_monat(durchlauf_ergebnisse):
    #Diagramm, die zeigt maximal Gewinn in jedem Monat
    x=[i for i in range(1, 13)]
    y=[durchlauf_ergebnis.maximaler_monatsgewinn(i) for durchlauf_ergebnis in durchlauf_ergebnisse for i in range(12)]
    options = {
    "xAxis": {"type": "category", "data": x},
    "yAxis": {"type": "value"},
    "series": [{"data": y, "type": "line"}],
    }
    st_echarts(options=options, height="400px")


def plot_diagram_durchschnittliche_gewinn_im_monat(durchlauf_ergebnisse):
    #Diagramm, die zeigt durchschnittliche Gewinn in jedem Monat
    x=[i for i in range(1, 13)]
    y=[durchlauf_ergebnis.durchschnittliche_monatsgewinn(i) for durchlauf_ergebnis in durchlauf_ergebnisse for i in range(12)]
    options = {
    "xAxis": {"type": "category", "data": x},
    "yAxis": {"type": "value"},
    "series": [{"data": y, "type": "line"}],
    }
    st_echarts(options=options, height="400px")


def plot_diagram_min_gewinn_im_monat(durchlauf_ergebnisse):
    #Diagramm, die zeigt maximal Gewinn in jedem Monat
    x=[i for i in range(1, 13)]
    y=[durchlauf_ergebnis.minimaler_monatsgewinn(i) for durchlauf_ergebnis in durchlauf_ergebnisse for i in range(12)]
    options = {
    "xAxis": {"type": "category", "data": x},
    "yAxis": {"type": "value"},
    "series": [{"data": y, "type": "line"}],
    }
    st_echarts(options=options, height="400px")

def diagram_tagesgewinn(jahresergebnis):
    #Diagramm, die zeigt Gewinn von jedem Tag
    x=[i for i in range(1, 366)]
    y=[jahresergebnis.tagesergebnis(i) for i in range(365)]
    options = {
    "xAxis": {"type": "category", "data": x},
    "yAxis": {"type": "value"},
    "series": [{"data": y}],
    }
    st_echarts(options=options, height="400px")


class DurchlaufErgebnis:
    def __init__(self, jahresergebnisse:list[Jahresergebnis]):
        self.jahresergebnisse = jahresergebnisse
        self._max_jahresergebnis = max(jahresergebnisse, key=lambda x: x.gewinn) if jahresergebnisse else None
        self._max_monatsgewinne = [jahresergebnis.monatsergebnis for jahresergebnis in jahresergebnisse]

    def maximaler_jahresgewinn(self):
        return max(jahresergebnis.gewinn for jahresergebnis in self.jahresergebnisse)
    
    def maximaler_monatsgewinn(self, monat):
        return max(jahresergebnis.monatsergebnis(monat).gewinn for jahresergebnis in self.jahresergebnisse)
    
    def minimaler_monatsgewinn(self, monat):
        return min(jahresergebnis.monatsergebnis(monat).gewinn for jahresergebnis in self.jahresergebnisse)
    
    def durchschnittliche_monatsgewinn(self, monat):
        return np.mean([jahresergebnis.monatsergebnis(monat).gewinn for jahresergebnis in self.jahresergebnisse])

    def sum_gewinne(self):
        return sum(jahresergebnis.gewinn for jahresergebnis in self.jahresergebnisse)
    
    def durchschnitt_gewinne(self):
        return self.sum_gewinne() / len(self.jahresergebnisse) if self.jahresergebnisse else 0
    
    def std_gewinne(self):
        return np.std([jahresergebnis.gewinn for jahresergebnis in self.jahresergebnisse], ddof=1) if self.jahresergebnisse else 0
    
    def varianz_gewinne(self):
        return np.var([jahresergebnis.gewinn for jahresergebnis in self.jahresergebnisse], ddof=1) if self.jahresergebnisse else 0
    
    def median_gewinne(self):
        return np.median([jahresergebnis.gewinn for jahresergebnis in self.jahresergebnisse]) if self.jahresergebnisse else 0
    

