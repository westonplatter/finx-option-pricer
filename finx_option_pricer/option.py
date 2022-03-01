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
    def _t_days(self) -> int:
        """Time in days"""
        return int(self.T * 365)

    @property
    def id(self) -> str:
        """Generate unique identifier for option contract as priced by respective algo"""
        id_values = [
            self.K,
            self._t_days,
            self.r,
            self.sigma,
            self.option_type,
            self.algo,
        ]
        return "-".join([str(x) for x in id_values])

    @property
    def value(self) -> float:
        """Option value wrt to algo"""
        func = None
        if self.option_type == "c":
            func = bsm.bs_call_value
        elif self.option_type == "p":
            func = bsm.bs_put_value
        return func(self.S, self.K, self.T, self.r, self.sigma)

    def final_value(self, price: float) -> float:
        """Final value of option at expiration"""
        v = self.value
        if self.option_type == "c":
            return np.max([price - self.K - v, -v])
        elif self.option_type == "p":
            return np.max([self.K - price - v, -v])

    @property
    def extrinsic_value(self) -> float:
        """Extrinsic value = option price - intrinsic value"""
        return self.value - self.intrinsic_value

    @property
    def intrinsic_value(self) -> float:
        """Intrinsic value = current (underlying) price - option price

        Returns:
            float: intrinsic value
        """
        return max(self.S - self.K, 0)

    @property
    def time_value(self) -> float:
        """Calc time value, defined as,
        Time Value = option value - intrinsic value
        https://www.investopedia.com/terms/t/timevalue.asp

        Returns:
            float: time_value
        """
        return self.value - self.intrinsic_value

    @property
    def delta(self) -> float:
        func = None
        if self.option_type == "c":
            func = bsm.delta_call
        elif self.option_type == "p":
            func = bsm.delta_put
        return func(self.S, self.K, self.T, self.r, self.sigma)

    @property
    def gamma(self) -> float:
        bsm.gamma(self.S, self.K, self.T, self.r, self.sigma)

    @property
    def vega(self) -> float:
        bsm.vega(self.S, self.K, self.T, self.r, self.sigma)

    @property
    def theta(self) -> float:
        func = None
        if self.option_type == "c":
            func = bsm.theta_call
        elif self.option_type == "p":
            func = bsm.theta_put
        return func(self.S, self.K, self.T, self.r, self.sigma)

    @property
    def rho(self) -> float:
        func = None
        if self.option_type == "c":
            func = bsm.rho_call
        elif self.option_type == "p":
            func = bsm.rho_put
        return func(self.S, self.K, self.T, self.r, self.sigma)
