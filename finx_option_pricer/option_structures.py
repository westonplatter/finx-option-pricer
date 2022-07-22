from typing import List

from finx_option_pricer.option import Option
from finx_option_pricer.option_plot import OptionPosition

MARKET_DAYS_PER_YEAR = 252
RATE_ZERO = 0.0


def annualized_days(days: int) -> float:
    "Convert days to years"
    return days / MARKET_DAYS_PER_YEAR


def gen_calendar(
    spot_price: float,
    strike_price: float,
    front_days: int,
    front_vol: float,
    front_vol_final: float,
    back_days: int,
    back_vol: float,
    back_vol_final: float,
    option_type: str = "c",
) -> List[OptionPosition]:
    """
    Generate a calendar structure

    Assumes
    - interest rate is 0.0

    Returns: List[OptionPosition]
    """
    fs = front_vol
    fsf = front_vol_final
    bs = back_vol
    bsf = back_vol_final

    front = OptionPosition(
        quantity=-1,
        end_sigma=fsf,
        option=Option(
            S=spot_price, K=strike_price, T=annualized_days(front_days), r=RATE_ZERO, sigma=fs, option_type=option_type
        ),
    )

    back = OptionPosition(
        quantity=+1,
        end_sigma=bsf,
        option=Option(
            S=spot_price, K=strike_price, T=annualized_days(back_days), r=RATE_ZERO, sigma=bs, option_type=option_type
        ),
    )

    return [front, back]


def gen_strangle(
    spot_price: float,
    strike_price: float,
    days: int,
    vol_initial: float,
    vol_final: float,
) -> List[OptionPosition]:
    """
    Generate strangle

    Assumes
    - interest rate is 0.0

    Returns: List[OptionPosition]
    """

    short_call = OptionPosition(
        quantity=-1,
        end_sigma=vol_final,
        option=Option(
            S=spot_price,
            K=strike_price,
            T=annualized_days(days),
            r=RATE_ZERO,
            sigma=vol_initial,
            option_type="c",
        ),
    )

    short_put = OptionPosition(
        quantity=-1,
        end_sigma=vol_final,
        option=Option(
            S=spot_price,
            K=strike_price,
            T=annualized_days(days),
            r=RATE_ZERO,
            sigma=vol_initial,
            option_type="p",
        ),
    )

    return [short_call, short_put]
