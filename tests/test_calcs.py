import numpy as np

from finx_option_pricer.calcs import calc_combined_call_put_iv


def test_calc_combined_call_put_iv():
    # got these numbers from IB for the /ES options
    S = 4095.0
    K = 4150.0
    fa, civ, piv = calc_combined_call_put_iv(S=S, K=K, call_price=108.5, put_price=80.25, time_days=16)

    expected_civ = 0.220535
    expected_piv = 0.222397
    expected_fa = 42

    assert fa == expected_fa
    np.testing.assert_almost_equal(civ, expected_civ, decimal=3)
    np.testing.assert_almost_equal(piv, expected_piv, decimal=3)
