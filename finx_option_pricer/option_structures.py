from finx_option_pricer.option_plot import OptionPosition
from finx_option_pricer.option import Option


MARKET_DAYS_PER_YEAR = 252

def gen_calendar(
    spot_price: float,
    strike_price: float, 
    front_days: int, 
    front_vol: float, 
    front_vol_final: float, 
    back_vol: float, 
    back_vol_final: float,
    option_type: str = 'c',
):
    """
    Generate a calendar structure
    
    Assumes
    (1) interest rate is 0.0
    (2) vol is constant over time

    
    """
    fs = front_vol
    fsf = front_vol_final
    bs = back_vol
    bsf = back_vol_final
    
    # convert days to decimal of years
    front_time = front_days/MARKET_DAYS_PER_YEAR
    back_time = (front_days+1)/MARKET_DAYS_PER_YEAR

    front = OptionPosition(
        quantity=-1, 
        end_sigma=fsf,
        option=Option(
            S=spot_price, 
            K=strike_price, 
            T=front_time, 
            r=0.0, 
            sigma=fs, 
            option_type=option_type
        )
    )
    
    back = OptionPosition(
        quantity=+1,
        end_sigma=bsf,
        option=Option(
            S=spot_price, 
            K=strike_price, 
            T=back_time, 
            r=0.0, 
            sigma=bs, 
            option_type=option_type
        )
    )

    return [front, back]