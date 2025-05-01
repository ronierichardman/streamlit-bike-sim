from scipy.stats import t
import numpy as np


class BoxplotData:
    def __init__(self, data):
        self.data = data
        self.median = np.median(data)
        self.unteres_quartil = np.percentile(data, 25)
        self.oberes_quartil = np.percentile(data, 75)
        self.iqr = self.oberes_quartil - self.unteres_quartil
        self.min = np.min(data)
        self.max = np.max(data)
        self.outliers = [x for x in data if x < self.unteres_quartil - 1.5 * self.iqr or x > self.oberes_quartil + 1.5 * self.iqr]

    def to_list(self):
        return [ 
            round(self.min, 2),
            round(self.unteres_quartil, 2),
            round(self.median, 2),
            round(self.oberes_quartil, 2),
            round(self.max, 2)
        ]

class ConfidenceInterval:
    def __init__(self, data):
        self.data = data
        self.n = len(data)
        self.mw = np.mean(data)
        self.std = np.std(data, ddof=1) # Sample standard deviation
        self.var = np.var(data, ddof=1)
        # Standard error
        self.sem = self.std / np.sqrt(self.n) if self.n > 1 else 0
        
        # t-critical value for 95% CI
        self.confidence_level = 0.95
        self.t_critical = t.ppf((1 + self.confidence_level) / 2, df=self.n - 1)
        
        # Confidence interval
        self.ci_lower = self.mw - self.t_critical * self.sem if self.n > 1 else self.mw
        self.ci_upper = self.mw + self.t_critical * self.sem if self.n > 1 else self.mw
        self.ci = (self.ci_lower, self.ci_upper)
        self.ci_str = f"[{round(self.ci_lower, 2)}, {round(self.ci_upper, 2)}]" if self.n > 1 else f"[{round(self.mw, 2)}]"

