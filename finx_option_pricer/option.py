from dataclasses import dataclass

import numpy as np

import finx_option_pricer.bsm as bsm


@dataclass
class Option:
    S: float  # current price
    K: float  # strike price
    T: float  # time to maturity (in years)
    r: float  # risk free rate
    # q: float # dividend rate
    sigma: float  # volatility
    option_type: str = "c"
    algo: str = "bsm"

    @property
    def id(self):
        tdays = int(self.T * 365)
        return f"{self.S}-{self.K}-{tdays}-{self.r}-{self.sigma}-{self.option_type}-{self.algo}"
    
    def final_value(self, price: float):
        v = self.value
        if self.option_type == 'c':
            return np.max([price - self.K - v, -v])
        elif self.option_type == "p":
            return np.max([self.K - price - v, -v])

    @property
    def value(self):
        func = None
        if self.option_type == "c":
            func = bsm.bs_call_value
        elif self.option_type == "p":
            func = bsm.bs_put_value
        return func(self.S, self.K, self.T, self.r, self.sigma)

    @property
    def delta(self):
        func = None
        if self.option_type == "c":
            func = bsm.delta_call
        elif self.option_type == "p":
            func = bsm.delta_put
        return func(self.S, self.K, self.T, self.r, self.sigma)

    @property
    def gamma(self):
        bsm.gamma(self.S, self.K, self.T, self.r, self.sigma)

    @property
    def vega(self):
        bsm.vega(self.S, self.K, self.T, self.r, self.sigma)

    @property
    def theta(self):
        func = None
        if self.option_type == "c":
            func = bsm.theta_call
        elif self.option_type == "p":
            func = bsm.theta_put
        return func(self.S, self.K, self.T, self.r, self.sigma)

    @property
    def rho(self):
        func = None
        if self.option_type == "c":
            func = bsm.rho_call
        elif self.option_type == "p":
            func = bsm.rho_put
        return func(self.S, self.K, self.T, self.r, self.sigma)
