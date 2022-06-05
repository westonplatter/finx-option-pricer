#
# pulled from codearmo.com
# https://www.codearmo.com/python-tutorial/options-trading-greeks-black-scholes
#
import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize_scalar

N = norm.cdf
N_prime = norm.pdf


def bs_call_value(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * N(d1) - K * np.exp(-r * T) * N(d2)


def bs_put_value(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return K * np.exp(-r * T) * N(-d2) - S * N(-d1)


def bs_calldiv_value(S, K, T, r, q, sigma):
    """Call with dividend value"""
    d1 = (np.log(S / K) + (r - q + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * np.exp(-q * T) * N(d1) - K * np.exp(-r * T) * N(d2)


def bs_putdiv_value(S, K, T, r, q, sigma):
    """Put with dividend value"""
    d1 = (np.log(S / K) + (r - q + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return K * np.exp(-r * T) * N(-d2) - S * np.exp(-q * T) * N(-d1)


def d1(S, K, T, r, sigma):
    return (np.log(S / K) + (r + sigma ** 2 / 2) * T) / sigma * np.sqrt(T)


def d2(S, K, T, r, sigma):
    return d1(S, K, T, r, sigma) - sigma * np.sqrt(T)


def delta_call(S, K, T, r, sigma):
    return N(d1(S, K, T, r, sigma))


def delta_put(S, K, T, r, sigma):
    return -N(-d1(S, K, T, r, sigma))


def gamma(S, K, T, r, sigma):
    return N_prime(d1(S, K, T, r, sigma)) / (S * sigma * np.sqrt(T))


def vega(S, K, T, r, sigma):
    return S * np.sqrt(T) * N_prime(d1(S, K, T, r, sigma))


def theta_call(S, K, T, r, sigma):
    p1 = -S * N_prime(d1(S, K, T, r, sigma)) * sigma / (2 * np.sqrt(T))
    p2 = r * K * np.exp(-r * T) * N(d2(S, K, T, r, sigma))
    return p1 - p2


def theta_put(S, K, T, r, sigma):
    p1 = -S * N_prime(d1(S, K, T, r, sigma)) * sigma / (2 * np.sqrt(T))
    p2 = r * K * np.exp(-r * T) * N(-d2(S, K, T, r, sigma))
    return p1 + p2


def rho_call(S, K, T, r, sigma):
    return K * T * np.exp(-r * T) * N(d2(S, K, T, r, sigma))


def rho_put(S, K, T, r, sigma):
    return -K * T * np.exp(-r * T) * N(-d2(S, K, T, r, sigma))


def implied_vol_call(opt_value, S, K, T, r):
    # https://www.codearmo.com/python-tutorial/calculating-volatility-smile
    def call_obj(sigma):
        return abs(bs_call_value(S, K, T, r, sigma) - opt_value)

    res = minimize_scalar(call_obj, bounds=(0.01, 6), method="bounded")
    return res.x


def implied_vol_put(opt_value, S, K, T, r):
    # https://www.codearmo.com/python-tutorial/calculating-volatility-smile
    def put_obj(sigma):
        return abs(bs_put_value(S, K, T, r, sigma) - opt_value)

    res = minimize_scalar(put_obj, bounds=(0.01, 6), method="bounded")
    return res.x
