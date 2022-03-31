from doctest import master
import math

from finx_option_pricer.option import Option


def test_intrinsic_value():
    # option is $1.0 in the money
    option = Option(S=90, K=89, T=0.5, r=0.0, sigma=0.3, option_type="c")
    expected_intrinsic_value = 90.0 - 89.0
    assert math.isclose(option.intrinsic_value, expected_intrinsic_value, abs_tol=0.01)

    # option is OTM, therefore, all extrinsic value
    option = Option(S=90, K=96, T=1 / 12, r=0.0, sigma=0.3, option_type="c")
    assert option.intrinsic_value == 0.0


def test_extrinsic_value():
    # option is $1.0 in the money, so remaining value is extrinsic
    option = Option(S=90, K=89, T=1 / 12, r=0.0, sigma=0.3, option_type="c")
    extrinsic_value = option.extrinsic_value
    expected_extrinsic_value = 2.62
    assert math.isclose(extrinsic_value, expected_extrinsic_value, abs_tol=0.01)

    # option is OTM, therefore, all extrinsic value
    option = Option(S=90, K=96, T=1 / 12, r=0.0, sigma=0.3, option_type="c")
    extrinsic_value = option.extrinsic_value
    expected_extrinsic_value = 1.06
    assert math.isclose(extrinsic_value, expected_extrinsic_value, abs_tol=0.01)


def test_break_even_value():
    option = Option(S=90, K=100, T=1 / 12, r=0.0, sigma=0.3, option_type="c")
    expected_value = 0.44
    assert math.isclose(option.value, expected_value, abs_tol=0.01)
    expected_break_even_value = 100.44
    assert math.isclose(option.break_even_value, expected_break_even_value, abs_tol=0.01)
