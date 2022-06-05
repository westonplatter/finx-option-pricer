import numpy as np
import pandas as pd

from finx_option_pricer.option import CALL, PUT, Option


def calc_combined_call_put_iv(
    S: float = None, K: float = None, call_price: float = None, put_price: float = None, time_days: int = None
):
    """Determine adjustment and Call/Put IV

    Inputs:
        S: Spot price
        K: Strike price
        call_price: executed call price
        put_price: executed put price
        time_days: DTE in (int) days

    Returns:
        Tuple: (price_adjustment, call_iv, put_iv)
    """
    fd = dict(T=time_days / 252.0, r=0.0, S=S, K=K, sigma=None)
    fc = {**fd, **dict(option_type=CALL)}
    fp = {**fd, **dict(option_type=PUT)}
    fco = Option(**fc)
    fpo = Option(**fp)
    results = []
    for i in range(0, 60):
        civ = fco.iv(call_price - i)
        piv = fpo.iv(put_price + i)
        results.append((i, civ, piv))

    df = pd.DataFrame(results, columns=["diff", "iv_call", "iv_put"]).set_index("diff")
    df["iv_diff"] = df["iv_call"] - df["iv_put"]
    pa = df[np.sign(df["iv_diff"]).diff().fillna(0).ne(0)].copy().index[0]
    fciv = fco.iv(call_price - pa)
    fpiv = fpo.iv(put_price + pa)
    return (pa, fciv, fpiv)
